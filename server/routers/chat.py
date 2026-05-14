import os
import re
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from openai import AsyncOpenAI
from langchain_core.output_parsers import StrOutputParser

from schemas import ChatRequest, ChatResponse, ChatMessage
from dependencies import verify_api_key
from routers.auth import get_current_user
import database, models
from ml.rag_engine import rag_engine
from ml.decision_engine import run_decision_engine
from ml.inference import predict_risk, predict_price, get_weather
from ml.expert_rules import run_expert_check
from config import LOCATION_MAPPING

load_dotenv()

router = APIRouter(
    prefix="/api",
    tags=["Chat"],
)

# LM Studio Configuration
LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://127.0.0.1:1234/v1")
CHAT_MODEL = os.getenv("CHAT_MODEL", "google/gemma-2-9b")
API_KEY_VAL = os.getenv("OPENROUTER_API_KEY", "lm-studio")

llm_client = None
if LM_STUDIO_URL:
    llm_client = AsyncOpenAI(
        base_url=LM_STUDIO_URL,
        api_key=API_KEY_VAL,
    )

_GREETING_WORDS = ["xin chào", "chào bạn", "chào", "hello", "hi", "hey", "alo"]
_THANKS_WORDS = ["cảm ơn", "cám ơn", "thanks", "thank you", "tạm biệt", "bye"]
_FINANCE_KEYWORDS = ["chi phí", "giá bao nhiêu", "tốn bao nhiêu", "đầu tư", "vốn", "lợi nhuận", "doanh thu", "roi"]

def classify_intent(message: str) -> str:
    msg = message.lower().strip()
    agri_keywords = ["cây", "trồng", "bón", "phân", "sâu", "bệnh", "tưới", "đất", "giống", "chăm sóc", "kỹ thuật", "cà phê", "sầu riêng", "chè", "trà"]
    
    if any(kw in msg for kw in _FINANCE_KEYWORDS):
        return "finance"
    if any(kw in msg for kw in agri_keywords) or len(msg) > 30:
        return "agriculture"

    if any(re.search(rf"\b{re.escape(g)}\b", msg) for g in _GREETING_WORDS): 
        return "greeting"
    if any(re.search(rf"\b{re.escape(t)}\b", msg) for t in _THANKS_WORDS): 
        return "thanks"
        
    return "agriculture"

def detect_crop_in_message(message: str) -> Optional[str]:
    msg = message.lower()
    crops = {"sầu riêng": "Sầu riêng Ri6", "robusta": "Cà phê Robusta", "arabica": "Cà phê Arabica", "chè": "Chè Ô Long", "trà": "Chè Ô Long"}
    for k, v in crops.items():
        if k in msg: return v
    return None

async def _get_rag_response(query: str) -> str:
    # Filter nội dung nhạy cảm
    query_lower = query.lower()
    forbidden = ["quên hết", "chính trị", "tôn giáo", "mã nguồn", "password"]
    if any(k in query_lower for k in forbidden):
        return "Xin lỗi, tôi chỉ hỗ trợ các vấn đề về kỹ thuật canh tác nông nghiệp tại Lâm Đồng."

    # Giảm top_k để tiết kiệm token và tránh Rate Limit cho tài khoản free
    context = rag_engine.get_relevant_context(query, top_k=3)
    
    # Nếu context quá yếu, AI vẫn nên cố gắng trả lời dựa trên kiến thức chung của nó
    # nhưng kèm theo cảnh báo là không tìm thấy trong tài liệu nội bộ.
    context_str = context if context else "Không có dữ liệu cụ thể trong sổ tay kỹ thuật."

    if API_KEY_VAL.startswith("AIza") and llm:
        prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "Bạn là 'Trợ Lý Thần Nông' - chuyên gia nông nghiệp tại Lâm Đồng.\n"
                "NHIỆM VỤ: Giải đáp kỹ thuật canh tác (Cà phê, Sầu riêng, Chè).\n\n"
                "NGỮ CẢNH HỖ TRỢ:\n{context}\n\n"
                "QUY TẮC:\n"
                "1. Ưu tiên thông tin trong NGỮ CẢNH.\n"
                "2. Nếu không có trong NGỮ CẢNH, hãy dùng kiến thức chuyên gia nhưng báo rõ: 'Dựa trên kinh nghiệm chung...'.\n"
                "3. TRẢ LỜI NGẮN GỌN, cô đọng, dùng gạch đầu dòng (Tối đa 150-200 từ).\n"
                "4. Luôn chúc bà con mùa màng bội thu.\n"
                "5. KHÔNG trả lời vấn đề ngoài nông nghiệp."
            )),
            ("human", "{query}")
        ])
        chain = prompt | llm | StrOutputParser()
        try:
            res = await chain.ainvoke({"query": query, "context": context_str})
            if res: return res
        except Exception as e:
            print(f"LLM Error: {e}")
            pass
    elif llm_client:
        try:
            response = await llm_client.chat.completions.create(
                model=CHAT_MODEL,
                messages=[
                    {"role": "system", "content": (
                        "Bạn là 'Trợ Lý Thần Nông' - chuyên gia nông nghiệp tại Lâm Đồng.\n"
                        f"NGỮ CẢNH HỖ TRỢ:\n{context_str}\n\n"
                        "QUY TẮC:\n"
                        "1. Ưu tiên thông tin trong NGỮ CẢNH.\n"
                        "2. TRẢ LỜI CỰC KỲ NGẮN GỌN, súc tích, tập trung vào giải pháp kỹ thuật.\n"
                        "3. Dùng gạch đầu dòng, tối đa 3-5 ý chính.\n"
                        "4. KHÔNG trả lời các vấn đề ngoài nông nghiệp."
                    )},
                    {"role": "user", "content": query}
                ],
                temperature=0.3,
                max_tokens=1024,
                extra_headers={
                    "HTTP-Referer": "http://localhost:8000",
                    "X-OpenRouter-Title": "Tro Ly Than Nong",
                }
            )
            res = response.choices[0].message.content
            if res:
                # Loại bỏ các thẻ suy nghĩ (thought) nếu model có trả về
                res = re.sub(r'<thought>.*?</thought>', '', res, flags=re.DOTALL)
                res = res.strip()
                return res
        except Exception as e:
            # Fallback cuối cùng: Trả về trực tiếp thông tin từ RAG nếu AI quá tải
            print(f"Chat API Error: {e}")
            if not context:
                return "Rất tiếc, hệ thống chưa tìm thấy thông tin kỹ thuật cụ thể. Bà con có thể thử hỏi lại với tên loại cây cụ thể (VD: bệnh rỉ sắt trên cà phê) nhé!"
                
            clean_context = context.replace(" . . .", "").replace("...", "").strip()
            return "⚠️ AI đang bận, tôi xin trích dẫn trực tiếp từ tài liệu kỹ thuật để bà con tham khảo ngay:\n\n" + clean_context + "\n\n(Lưu ý: Đây là dữ liệu gốc từ sổ tay hướng dẫn)."

def _run_finance_simulation(crop: str, capital: float, area_ha: float, location: str, mode: str) -> str:
    loc_info = LOCATION_MAPPING.get(location, LOCATION_MAPPING["Phường B'Lao"])
    weather = get_weather(location)
    expert = run_expert_check(crop, location, loc_info["elevation"], weather["temp_max"], weather["temp_min"], weather["precipitation"])
    risk_level, _ = predict_risk(location, crop)
    current_price_map = {"Cà phê Robusta": 120000, "Cà phê Arabica": 150000, "Sầu riêng Ri6": 70000, "Chè Ô Long": 250000}
    cur_price = current_price_map.get(crop, 50000)
    forecast_data = predict_price(crop, cur_price, location)
    pred_30d = forecast_data[-1]["predicted"]
    
    res = run_decision_engine(crop, risk_level, cur_price, pred_30d, capital, area_ha, weather["temp_min"], weather["precipitation"], mode, expert["ecology_violation"])
    fa = res["financial_analysis"]
    def fmt_money(v): return f"{v/1_000_000:.0f} triệu" if v < 1_000_000_000 else f"{v/1_000_000_000:.1f} tỷ"
    
    return (
        f"Phân tích tài chính cho **{crop}** tại **{location}** ({area_ha} ha):\n"
        f"• Chi phí đầu tư: {fmt_money(fa['estimated_cost'])}\n"
        f"• Doanh thu dự tính: {fmt_money(fa['estimated_revenue'])}\n"
        f"• Lợi nhuận dự kiến: {fmt_money(fa['estimated_profit'])}\n"
        f"• ROI: {fa['roi_pct']:.1f}%\n\n"
        f"**Khuyến nghị**: {res['production_decision']['recommendation']}"
    )

@router.post("/chat", response_model=ChatResponse, dependencies=[Depends(verify_api_key)])
async def chat(request: ChatRequest, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    try:
        message = request.message.strip()
        if not message: return ChatResponse(answer="Bạn cần hỗ trợ gì không?", suggestions=["Kỹ thuật bón phân?", "Giá sầu riêng?"])
        
        msg_low = message.lower()
        forbidden = ["chính trị", "tôn giáo", "mã nguồn", "password"]
        if any(f in msg_low for f in forbidden):
            return ChatResponse(
                answer="Hệ thống chỉ hỗ trợ các câu hỏi liên quan đến nông nghiệp. Cảm ơn bạn.",
                suggestions=["Kỹ thuật trồng sầu riêng", "Giá cà phê hôm nay"]
            )

        intent = classify_intent(message)
        
        if intent == "greeting":
            answer = "Chào bạn! Tôi là hệ thống hỗ trợ nông nghiệp. Bạn cần tìm hiểu về kỹ thuật hay giá cả nông sản không?"
            suggestions = ["Chi phí trồng sầu riêng?", "Kỹ thuật bón phân?"]
        elif intent == "thanks":
            answer = "Rất vui được hỗ trợ bạn! Chúc bạn mùa màng thuận lợi. 🌾"
            suggestions = ["Hỏi về sâu bệnh", "Hỏi về giá cả"]
        elif intent == "finance":
            crop = detect_crop_in_message(message) or (request.context.crop if request.context else "Sầu riêng Ri6")
            loc = request.context.location if request.context else "Phường B'Lao"
            cap = request.context.capital if request.context and request.context.capital else 200_000_000
            area = request.context.area_ha if request.context and request.context.area_ha else 1.0
            mode = request.context.mode if request.context and request.context.mode else "Kinh doanh"
            answer = _run_finance_simulation(crop, cap, area, loc, mode)
            suggestions = ["Rủi ro thời tiết?", "Kỹ thuật chăm sóc?"]
        else:
            answer = await _get_rag_response(message)
            suggestions = ["Bón phân thế nào?", "Phòng trừ sâu bệnh?"]
        
        new_chat = models.ChatHistory(
            user_id=current_user.id,
            question=message,
            answer=answer
        )
        db.add(new_chat)
        db.commit()
        
        return ChatResponse(answer=answer, suggestions=suggestions)
    except Exception as e:
        print(f"Chat Error: {e}")
        raise HTTPException(status_code=500, detail="Lỗi hệ thống")

@router.get("/chat/history")
async def get_chat_history(current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    history = db.query(models.ChatHistory).filter(
        models.ChatHistory.user_id == current_user.id
    ).order_by(models.ChatHistory.created_at.asc()).limit(50).all()
    return history
