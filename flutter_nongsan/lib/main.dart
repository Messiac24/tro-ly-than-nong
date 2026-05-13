import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:lucide_icons/lucide_icons.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:ui';

void main() {
  runApp(const ThanNongApp());
}

class ThanNongApp extends StatelessWidget {
  const ThanNongApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Trợ Lý Thần Nông',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        primaryColor: const Color(0xFF2D6A4F),
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF2D6A4F),
          primary: const Color(0xFF2D6A4F),
          secondary: const Color(0xFF40916C),
          surface: Colors.white,
        ),
        scaffoldBackgroundColor: const Color(0xFFF8F9F0),
        textTheme: GoogleFonts.beVietnamProTextTheme(),
      ),
      home: const AuthWrapper(),
    );
  }
}

// ── Shared State ──────────────────────────────────────────────
class AppState {
  static String? selectedLocation;
  static String? selectedCrop;
}

// ── Auth Service ──────────────────────────────────────────────
class AuthService {
  static String? _token;
  static String? _fullName;

  static String get baseUrl => 'http://10.0.2.2:8000/api'; 
  static String get apiKey => 'dev-key-ai-nong-san-2026';

  static bool get isAuthenticated => _token != null;
  static String? get token => _token;
  static String? get fullName => _fullName;

  static Future<Map<String, dynamic>> login(String username, String password) async {
    try {
      // API Login sử dụng OAuth2PasswordRequestForm nên cần gửi x-www-form-urlencoded
      final response = await http.post(
        Uri.parse('$baseUrl/auth/login'),
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-API-Key': apiKey,
        },
        body: {
          'username': username,
          'password': password,
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        _token = data['access_token'];
        _fullName = data['full_name'];
        return {'success': true};
      } else {
        final error = jsonDecode(utf8.decode(response.bodyBytes));
        return {'success': false, 'message': error['detail'] ?? 'Lỗi đăng nhập'};
      }
    } catch (e) {
      return {'success': false, 'message': 'Lỗi kết nối máy chủ: $e'};
    }
  }

  static Future<Map<String, dynamic>> register({
    required String username,
    required String password,
    required String fullName,
    String? email,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/register'),
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': apiKey,
        },
        body: jsonEncode({
          'username': username,
          'password': password,
          'full_name': fullName,
          'email': email,
          'role': 'farmer',
        }),
      );

      if (response.statusCode == 200) {
        return {'success': true};
      } else {
        final error = jsonDecode(utf8.decode(response.bodyBytes));
        return {'success': false, 'message': error['detail'] ?? 'Lỗi đăng ký'};
      }
    } catch (e) {
      return {'success': false, 'message': 'Lỗi kết nối: $e'};
    }
  }
}

// ── Auth Wrapper ──────────────────────────────────────────────
class AuthWrapper extends StatefulWidget {
  const AuthWrapper({super.key});
  @override
  State<AuthWrapper> createState() => _AuthWrapperState();
}

class _AuthWrapperState extends State<AuthWrapper> {
  bool _isLoggedIn = false;
  void _onLoginSuccess() => setState(() => _isLoggedIn = true);

  @override
  Widget build(BuildContext context) {
    if (_isLoggedIn) return const MainScreen();
    return LoginScreen(onLoginSuccess: _onLoginSuccess);
  }
}

// ── Login Screen ──────────────────────────────────────────────
class LoginScreen extends StatefulWidget {
  final VoidCallback onLoginSuccess;
  const LoginScreen({super.key, required this.onLoginSuccess});
  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _userController = TextEditingController();
  final _passController = TextEditingController();
  bool _isLoading = false;

  void _handleLogin() async {
    setState(() => _isLoading = true);
    final result = await AuthService.login(_userController.text, _passController.text);
    setState(() => _isLoading = false);
    
    if (result['success']) {
      widget.onLoginSuccess();
    } else {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(result['message'])));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(gradient: LinearGradient(colors: [Color(0xFFD8F3DC), Color(0xFFF8F9F0)])),
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(32),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(32),
              child: BackdropFilter(
                filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
                child: Container(
                  padding: const EdgeInsets.all(32),
                  decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.6), border: Border.all(color: Colors.white.withValues(alpha: 0.5))),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Text('🌾', style: TextStyle(fontSize: 50)),
                      const SizedBox(height: 16),
                      Text('Đăng Nhập', style: GoogleFonts.beVietnamPro(fontSize: 24, fontWeight: FontWeight.w800, color: const Color(0xFF1B4332))),
                      const SizedBox(height: 32),
                      _field('Tên đăng nhập', _userController, LucideIcons.user, false),
                      const SizedBox(height: 16),
                      _field('Mật khẩu', _passController, LucideIcons.lock, true),
                      const SizedBox(height: 32),
                      _btn(_isLoading ? 'Đang xử lý...' : 'Đăng nhập', _isLoading ? null : _handleLogin),
                      const SizedBox(height: 16),
                      TextButton(
                        onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => RegisterScreen())),
                        child: const Text('Chưa có tài khoản? Đăng ký ngay', style: TextStyle(color: Color(0xFF2D6A4F))),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _field(String h, TextEditingController c, IconData i, bool p) => TextField(controller: c, obscureText: p, decoration: InputDecoration(prefixIcon: Icon(i, size: 18), hintText: h, filled: true, fillColor: Colors.white70, border: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: BorderSide.none)));
  Widget _btn(String l, VoidCallback? o) => SizedBox(width: double.infinity, height: 56, child: ElevatedButton(onPressed: o, style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF2D6A4F), foregroundColor: Colors.white, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16))), child: Text(l, style: const TextStyle(fontWeight: FontWeight.bold))));
}

// ── Register Screen ───────────────────────────────────────────
class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});
  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _userController = TextEditingController();
  final _passController = TextEditingController();
  final _nameController = TextEditingController();
  bool _isLoading = false;

  void _handleRegister() async {
    if (_userController.text.isEmpty || _passController.text.isEmpty || _nameController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Vui lòng nhập đầy đủ thông tin')));
      return;
    }
    setState(() => _isLoading = true);
    final result = await AuthService.register(
      username: _userController.text,
      password: _passController.text,
      fullName: _nameController.text,
    );
    setState(() => _isLoading = false);

    if (result['success']) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Đăng ký thành công! Hãy đăng nhập.')));
      Navigator.pop(context);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(result['message'])));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(backgroundColor: Colors.transparent, elevation: 0),
      extendBodyBehindAppBar: true,
      body: Container(
        decoration: const BoxDecoration(gradient: LinearGradient(colors: [Color(0xFFD8F3DC), Color(0xFFF8F9F0)])),
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(32),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(32),
              child: BackdropFilter(
                filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
                child: Container(
                  padding: const EdgeInsets.all(32),
                  decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.6), border: Border.all(color: Colors.white.withValues(alpha: 0.5))),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text('Đăng Ký', style: GoogleFonts.beVietnamPro(fontSize: 24, fontWeight: FontWeight.w800, color: const Color(0xFF1B4332))),
                      const SizedBox(height: 32),
                      _field('Họ và tên', _nameController, LucideIcons.userPlus, false),
                      const SizedBox(height: 16),
                      _field('Tên đăng nhập', _userController, LucideIcons.user, false),
                      const SizedBox(height: 16),
                      _field('Mật khẩu', _passController, LucideIcons.lock, true),
                      const SizedBox(height: 32),
                      _btn(_isLoading ? 'Đang xử lý...' : 'Đăng ký tài khoản', _isLoading ? null : _handleRegister),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
  Widget _field(String h, TextEditingController c, IconData i, bool p) => TextField(controller: c, obscureText: p, decoration: InputDecoration(prefixIcon: Icon(i, size: 18), hintText: h, filled: true, fillColor: Colors.white70, border: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: BorderSide.none)));
  Widget _btn(String l, VoidCallback? o) => SizedBox(width: double.infinity, height: 56, child: ElevatedButton(onPressed: o, style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF2D6A4F), foregroundColor: Colors.white, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16))), child: Text(l, style: const TextStyle(fontWeight: FontWeight.bold))));
}

// ── Main Screens & Others (Keep previous logic) ────────────────
class MainScreen extends StatefulWidget {
  const MainScreen({super.key});
  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _selectedIndex = 0;
  final List<Widget> _pages = [const AnalysisPage(), const ChatPage(), const DashboardPage()];
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _pages[_selectedIndex],
      bottomNavigationBar: Container(
        margin: const EdgeInsets.all(20),
        decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.8), borderRadius: BorderRadius.circular(30), boxShadow: [BoxShadow(color: Colors.black12, blurRadius: 20)]),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(30),
          child: NavigationBar(height: 65, backgroundColor: Colors.transparent, selectedIndex: _selectedIndex, onDestinationSelected: (i) => setState(() => _selectedIndex = i),
            destinations: const [
              NavigationDestination(icon: Icon(LucideIcons.barChart2), label: 'Phân tích'),
              NavigationDestination(icon: Icon(LucideIcons.messageCircle), label: 'Trợ lý AI'),
              NavigationDestination(icon: Icon(LucideIcons.layoutDashboard), label: 'Hệ thống'),
            ],
          ),
        ),
      ),
    );
  }
}

class AnalysisPage extends StatefulWidget {
  const AnalysisPage({super.key});
  @override
  State<AnalysisPage> createState() => _AnalysisPageState();
}

class _AnalysisPageState extends State<AnalysisPage> {
  String? _selectedLoc;
  String? _selectedCrop;
  bool _isLoading = false;
  Map<String, dynamic>? _result;
  final List<String> _locs = ["Phường B'Lao", "Phường Xuân Trường"];
  final List<String> _crops = ["Cà phê Robusta", "Cà phê Arabica", "Sầu riêng Ri6", "Chè Ô Long"];

  Future<void> _analyze() async {
    if (_selectedLoc == null || _selectedCrop == null) return;
    setState(() { _isLoading = true; AppState.selectedLocation = _selectedLoc; AppState.selectedCrop = _selectedCrop; });
    try {
      final res = await http.post(Uri.parse('${AuthService.baseUrl}/predict'),
        headers: {'Content-Type': 'application/json', 'X-API-Key': AuthService.apiKey, 'Authorization': 'Bearer ${AuthService.token}'},
        body: jsonEncode({'location': _selectedLoc, 'crop': _selectedCrop, 'capital': 100000000, 'area_ha': 1.0}),
      );
      if (res.statusCode == 200) setState(() => _result = jsonDecode(utf8.decode(res.bodyBytes)));
    } catch (e) { debugPrint(e.toString()); }
    setState(() => _isLoading = false);
  }

  @override
  Widget build(BuildContext context) {
    return CustomScrollView(
      slivers: [
        SliverAppBar(expandedHeight: 120, pinned: true, flexibleSpace: FlexibleSpaceBar(title: Text('Phân tích AI', style: GoogleFonts.beVietnamPro(fontWeight: FontWeight.w800, color: const Color(0xFF1B4332))), background: Container(decoration: const BoxDecoration(gradient: LinearGradient(colors: [Color(0xFFD8F3DC), Color(0xFFF8F9F0)]))))),
        SliverPadding(padding: const EdgeInsets.all(20), sliver: SliverList(delegate: SliverChildListDelegate([
              _buildInputCard(),
              if (_result != null) ...[
                const SizedBox(height: 24),
                _buildWeatherStat(_result!['location_info']),
                const SizedBox(height: 16),
                _buildRecommendation(_result!['action_plan']),
                if (_result!['financial_analysis'] != null) ...[const SizedBox(height: 16), _buildFinance(_result!['financial_analysis'])],
              ] else if (!_isLoading) _buildEmptyState(),
              const SizedBox(height: 120),
            ])))
      ],
    );
  }

  Widget _buildInputCard() => Container(padding: const EdgeInsets.all(24), decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(28), boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.04), blurRadius: 24)]),
      child: Column(children: [
          _dropdown('Vùng canh tác', _selectedLoc, _locs, (v) => setState(() => _selectedLoc = v)),
          const SizedBox(height: 16),
          _dropdown('Cây trồng dự kiến', _selectedCrop, _crops, (v) => setState(() => _selectedCrop = v)),
          const SizedBox(height: 24),
          SizedBox(width: double.infinity, height: 56, child: ElevatedButton(onPressed: _isLoading ? null : _analyze, style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF2D6A4F), foregroundColor: Colors.white, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16))), child: _isLoading ? const CircularProgressIndicator(color: Colors.white) : const Text('Phân tích hệ thống', style: TextStyle(fontWeight: FontWeight.bold)))),
        ]));

  Widget _dropdown(String l, String? v, List<String> i, ValueChanged<String?> o) => Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(l, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Color(0xFF1B4332))), const SizedBox(height: 8), DropdownButtonFormField<String>(value: v, decoration: InputDecoration(filled: true, fillColor: const Color(0xFFF8F9F0), border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none)), items: i.map((e) => DropdownMenuItem(value: e, child: Text(e))).toList(), onChanged: o)]);
  Widget _buildWeatherStat(Map<String, dynamic> i) => Container(padding: const EdgeInsets.all(20), decoration: BoxDecoration(color: const Color(0xFF2D6A4F), borderRadius: BorderRadius.circular(24)), child: Row(mainAxisAlignment: MainAxisAlignment.spaceAround, children: [_stat(LucideIcons.thermometer, '${i['current_temp']}°C', 'Nhiệt độ'), _stat(LucideIcons.droplets, '${i['recent_rainfall_mm']}mm', 'Lượng mưa'), _stat(LucideIcons.mountain, '${i['elevation']}m', 'Độ cao')]));
  Widget _stat(IconData i, String v, String l) => Column(children: [Icon(i, color: Colors.white70, size: 20), const SizedBox(height: 4), Text(v, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)), Text(l, style: const TextStyle(color: Colors.white54, fontSize: 10))]);
  Widget _buildRecommendation(Map<String, dynamic> p) {
    final c = p['level'] == 'danger' ? Colors.red : (p['level'] == 'warning' ? Colors.orange : Colors.green);
    return Container(padding: const EdgeInsets.all(24), decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(24), border: Border.all(color: c.withValues(alpha: 0.1), width: 2)), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Row(children: [Icon(LucideIcons.alertCircle, color: c), const SizedBox(width: 8), Text('KHUYẾN NGHỊ: ${p['level'].toString().toUpperCase()}', style: TextStyle(color: c, fontWeight: FontWeight.bold, fontSize: 12))]), const SizedBox(height: 12), Text(p['message'], style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15)), const SizedBox(height: 8), Text(p['reasoning'] ?? '', style: const TextStyle(color: Colors.grey, fontSize: 13))]));
  }
  Widget _buildFinance(Map<String, dynamic> f) => Container(padding: const EdgeInsets.all(24), decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(24)), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [const Text('Phân tích tài chính', style: TextStyle(fontWeight: FontWeight.bold)), const SizedBox(height: 16), _finRow('Vốn đầu tư', '${f['estimated_cost'] / 1000000} triệu'), _finRow('Doanh thu dự kiến', '${f['estimated_revenue'] / 1000000} triệu'), const Divider(), _finRow('ROI kỳ vọng', '${f['roi_pct']}%', highlight: true)]));
  Widget _finRow(String l, String v, {bool highlight = false}) => Padding(padding: const EdgeInsets.symmetric(vertical: 6), child: Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [Text(l, style: const TextStyle(color: Colors.grey)), Text(v, style: TextStyle(fontWeight: FontWeight.bold, color: highlight ? const Color(0xFF2D6A4F) : null))]));
  Widget _buildEmptyState() => Center(child: Padding(padding: const EdgeInsets.only(top: 80), child: Column(children: [Icon(LucideIcons.search, size: 48, color: Colors.grey.shade300), const SizedBox(height: 16), Text('Chọn thông tin để AI phân tích', style: TextStyle(color: Colors.grey.shade400))])));
}

class ChatPage extends StatefulWidget {
  const ChatPage({super.key});
  @override
  State<ChatPage> createState() => _ChatPageState();
}

class _ChatPageState extends State<ChatPage> {
  final _controller = TextEditingController();
  final List<Map<String, dynamic>> _messages = [{'text': 'Chào bạn! Tôi là trợ lý AI nông nghiệp. Bạn cần giúp gì?', 'isAssistant': true}];
  bool _isLoading = false;
  final _scroll = ScrollController();

  Future<void> _send() async {
    final text = _controller.text.trim();
    if (text.isEmpty) return;
    setState(() { _messages.add({'text': text, 'isAssistant': false}); _isLoading = true; _controller.clear(); });
    _scrollToBottom();
    try {
      final res = await http.post(Uri.parse('${AuthService.baseUrl}/chat'),
        headers: {'Content-Type': 'application/json', 'X-API-Key': AuthService.apiKey, 'Authorization': 'Bearer ${AuthService.token}'},
        body: jsonEncode({'message': text, 'history': [], 'context': {'location': AppState.selectedLocation ?? "Phường B'Lao", 'crop': AppState.selectedCrop ?? "Cà phê Robusta"}}),
      );
      if (res.statusCode == 200) setState(() => _messages.add({'text': jsonDecode(utf8.decode(res.bodyBytes))['answer'], 'isAssistant': true}));
    } catch (e) { debugPrint(e.toString()); }
    setState(() => _isLoading = false);
    _scrollToBottom();
  }
  void _scrollToBottom() => Future.delayed(const Duration(milliseconds: 100), () { if (_scroll.hasClients) _scroll.animateTo(_scroll.position.maxScrollExtent, duration: const Duration(milliseconds: 300), curve: Curves.easeOut); });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Trợ lý AI'), centerTitle: true, elevation: 0),
      body: Column(
        children: [
          Expanded(child: ListView.builder(controller: _scroll, padding: const EdgeInsets.all(20), itemCount: _messages.length + (_isLoading ? 1 : 0), itemBuilder: (context, i) {
                if (i == _messages.length) return const Center(child: Padding(padding: EdgeInsets.all(16), child: CircularProgressIndicator()));
                final m = _messages[i];
                return _ChatBubble(message: m['text'], isAssistant: m['isAssistant']);
              })),
          Container(padding: const EdgeInsets.fromLTRB(20, 12, 20, 100), color: Colors.white, child: Row(children: [
                Expanded(child: TextField(controller: _controller, decoration: const InputDecoration(hintText: 'Hỏi chuyên gia...', border: InputBorder.none))),
                const SizedBox(width: 12),
                IconButton(onPressed: _isLoading ? null : _send, icon: const Icon(LucideIcons.send, color: Color(0xFF2D6A4F))),
              ])),
        ],
      ),
    );
  }
}

class _ChatBubble extends StatelessWidget {
  final String message;
  final bool isAssistant;
  const _ChatBubble({required this.message, required this.isAssistant});
  @override
  Widget build(BuildContext context) {
    return Align(alignment: isAssistant ? Alignment.centerLeft : Alignment.centerRight, child: Container(padding: const EdgeInsets.all(16), margin: const EdgeInsets.only(bottom: 12), constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.75),
        decoration: BoxDecoration(color: isAssistant ? Colors.white : const Color(0xFF2D6A4F), borderRadius: BorderRadius.only(topLeft: const Radius.circular(20), topRight: const Radius.circular(20), bottomLeft: Radius.circular(isAssistant ? 0 : 20), bottomRight: Radius.circular(isAssistant ? 20 : 0)), boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.05), blurRadius: 10)]),
        child: Text(message, style: TextStyle(color: isAssistant ? Colors.black : Colors.white, height: 1.4))));
  }
}

class DashboardPage extends StatelessWidget {
  const DashboardPage({super.key});
  @override
  Widget build(BuildContext context) {
    return CustomScrollView(
      slivers: [
        SliverAppBar(expandedHeight: 120, pinned: true, flexibleSpace: FlexibleSpaceBar(title: Text('Quản trị hệ thống', style: GoogleFonts.beVietnamPro(fontWeight: FontWeight.w800, color: const Color(0xFF1B4332))), background: Container(decoration: const BoxDecoration(gradient: LinearGradient(colors: [Color(0xFFE8F3E8), Color(0xFFF8F9F0)]))))),
        SliverPadding(padding: const EdgeInsets.all(20), sliver: SliverList(delegate: SliverChildListDelegate([
              const Text('Thống kê nhanh', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
              const SizedBox(height: 16),
              SingleChildScrollView(scrollDirection: Axis.horizontal, child: Row(children: [_buildStat('Người dùng', '1.2k', const Color(0xFF2D6A4F)), const SizedBox(width: 12), _buildStat('Nông dân', '1.1k', const Color(0xFF52B788)), const SizedBox(width: 12), _buildStat('Cảnh báo', '5', const Color(0xFFF4A261))])),
              const SizedBox(height: 32),
              const Text('Quản lý tri thức RAG', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
              const SizedBox(height: 16),
              Container(padding: const EdgeInsets.all(24), decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(24), border: Border.all(color: const Color(0xFFD8F3DC))), child: Column(children: [const Icon(LucideIcons.uploadCloud, size: 40, color: Color(0xFF40916C)), const SizedBox(height: 12), const Text('Cập nhật tri thức mới cho AI', style: TextStyle(fontWeight: FontWeight.bold)), const SizedBox(height: 4), const Text('Hỗ trợ định dạng PDF, DOCX', style: TextStyle(color: Colors.grey, fontSize: 12)), const SizedBox(height: 20), ElevatedButton(onPressed: () {}, style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF2D6A4F), foregroundColor: Colors.white), child: const Text('Tải tài liệu lên'))])),
              const SizedBox(height: 120),
            ])))
      ],
    );
  }
  Widget _buildStat(String l, String v, Color c) => Container(width: 130, padding: const EdgeInsets.all(20), decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(20), border: Border(left: BorderSide(color: c, width: 4))), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(l, style: const TextStyle(fontSize: 10, color: Colors.grey)), const SizedBox(height: 4), Text(v, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold))]));
}
