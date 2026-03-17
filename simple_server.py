#!/usr/bin/env python
"""
Simple HTTP Server for AI Business Idea Validator
Bypasses Django issues and provides direct access
"""

import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse
import json
from pathlib import Path

class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        path = self.path
        
        # Route to different pages
        if path == '/' or path == '/login':
            self.serve_login_page()
        elif path == '/demo':
            self.serve_demo_page()
        elif path.startswith('/static/'):
            self.serve_static_file(path)
        else:
            self.send_404()
    
    def do_POST(self):
        """Handle POST requests for login"""
        if path == '/login':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            post_data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            
            username = post_data.get('username', [''])[0]
            password = post_data.get('password', [''])[0]
            
            # Check demo credentials
            if username == 'demo' and password == 'demo123':
                # Redirect to demo page
                self.send_response(302, 'Found', [('Location', '/demo')])
            else:
                # Show error
                self.serve_login_page(error='Invalid username or password')
        else:
            self.send_404()
    
    def serve_login_page(self, error=None):
        """Serve the login page"""
        html = self.get_login_html(error)
        self.send_response(200, 'OK', [('Content-Type', 'text/html')], html)
    
    def serve_demo_page(self):
        """Serve the demo page"""
        html = self.get_demo_html()
        self.send_response(200, 'OK', [('Content-Type', 'text/html')], html)
    
    def serve_static_file(self, path):
        """Serve static files"""
        try:
            # Remove /static/ prefix
            static_path = path[8:]
            file_path = Path(__file__).parent / 'static' / static_path
            
            if file_path.exists() and file_path.is_file():
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                # Determine content type
                if static_path.endswith('.css'):
                    content_type = 'text/css'
                elif static_path.endswith('.js'):
                    content_type = 'application/javascript'
                elif static_path.endswith('.ico'):
                    content_type = 'image/x-icon'
                else:
                    content_type = 'text/plain'
                
                self.send_response(200, 'OK', [('Content-Type', content_type)], content)
            else:
                self.send_404()
        except Exception as e:
            self.send_404()
    
    def send_response(self, status_code, status_text, headers, content):
        """Send HTTP response"""
        self.send_response(status_code, status_text)
        
        for header, value in headers:
            self.send_header(header, value)
        
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))
    
    def send_404(self):
        """Send 404 response"""
        self.send_response(404, 'Not Found', [('Content-Type', 'text/html')], 
            '<html><body><h1>404 - Page Not Found</h1></body></html>')
    
    def get_login_html(self, error=None):
        """Generate login page HTML"""
        error_html = ''
        if error:
            error_html = f'''
            <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 8px; padding: 12px; margin-bottom: 20px; color: #ef4444;">
                <i class="fas fa-exclamation-triangle"></i> {error}
            </div>
            '''
        
        return f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - AI Business Idea Validator</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{
            --primary: #7C3AED;
            --secondary: #2563EB;
            --accent: #06B6D4;
            --success: #10B981;
            --danger: #EF4444;
            --dark-bg: #0F172A;
            --darker-bg: #020617;
            --glass-bg: rgba(255, 255, 255, 0.05);
            --glass-border: rgba(255, 255, 255, 0.1);
            --text-primary: #F8FAFC;
            --text-secondary: #CBD5E1;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            background: linear-gradient(135deg, var(--darker-bg) 0%, var(--dark-bg) 25%, #1a1f3a 50%, var(--dark-bg) 75%, var(--darker-bg) 100%);
            min-height: 100vh;
            color: var(--text-primary);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}

        .container {{
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 20px;
        }}

        .login-card {{
            background: var(--glass-bg);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--glass-border);
            border-radius: 24px;
            padding: 40px;
            width: 100%;
            max-width: 420px;
            box-shadow: 0 20px 40px rgba(124, 58, 237, 0.3);
        }}

        .logo {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--primary), var(--accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 30px;
        }}

        .title {{
            font-size: 1.8rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 30px;
            background: linear-gradient(135deg, var(--primary), var(--accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .form-group {{
            margin-bottom: 25px;
        }}

        .form-label {{
            display: block;
            font-size: 0.9rem;
            font-weight: 500;
            color: var(--text-secondary);
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .form-input {{
            width: 100%;
            padding: 15px 20px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--glass-border);
            border-radius: 12px;
            color: var(--text-primary);
            font-size: 1rem;
            transition: all 0.3s ease;
        }}

        .form-input:focus {{
            outline: none;
            border-color: var(--accent);
            box-shadow: 0 0 20px rgba(6, 182, 212, 0.3);
        }}

        .login-button {{
            width: 100%;
            background: linear-gradient(135deg, var(--primary), var(--accent));
            border: none;
            border-radius: 12px;
            color: white;
            font-size: 1.1rem;
            font-weight: 600;
            padding: 15px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 10px 25px rgba(124, 58, 237, 0.4);
        }}

        .login-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 0 40px rgba(124, 58, 237, 0.6);
        }}

        .demo-button {{
            width: 100%;
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 12px;
            color: var(--text-primary);
            font-size: 1rem;
            font-weight: 500;
            padding: 12px;
            margin-top: 15px;
            cursor: pointer;
            transition: all 0.3s ease;
        }}

        .demo-button:hover {{
            transform: translateY(-2px);
            background: rgba(124, 58, 237, 0.1);
            border-color: var(--primary);
        }}

        .footer {{
            text-align: center;
            margin-top: 30px;
            color: var(--text-secondary);
            font-size: 0.8rem;
            opacity: 0.7;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="login-card">
            <div class="logo">
                <i class="fas fa-brain"></i>
                <span>AI</span>
            </div>
            
            <h2 class="title">Welcome Back</h2>
            
            {error_html}
            
            <form method="post" action="/login">
                <div class="form-group">
                    <label class="form-label" for="username">Username</label>
                    <input type="text" id="username" name="username" class="form-input" placeholder="Enter your username" required>
                </div>
                
                <div class="form-group">
                    <label class="form-label" for="password">Password</label>
                    <input type="password" id="password" name="password" class="form-input" placeholder="Enter your password" required>
                </div>
                
                <button type="submit" class="login-button">
                    <i class="fas fa-sign-in-alt"></i>
                    Login
                </button>
                
                <button type="button" class="demo-button" onclick="demoLogin()">
                    <i class="fas fa-rocket"></i>
                    Demo Login
                </button>
            </form>
            
            <div class="footer">
                <p>Demo Credentials: username: <strong>demo</strong>, password: <strong>demo123</strong></p>
            </div>
        </div>
    </div>

    <script>
        function demoLogin() {{
            document.getElementById('username').value = 'demo';
            document.getElementById('password').value = 'demo123';
            document.querySelector('form').submit();
        }}
    </script>
</body>
</html>
        '''
    
    def get_demo_html(self):
        """Generate demo page HTML"""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Demo - AI Business Idea Validator</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body {{
            background: linear-gradient(135deg, #020617 0%, #0F172A 25%, #1a1f3a 50%, #0F172A 75%, #020617 100%);
            min-height: 100vh;
            color: #F8FAFC;
            font-family: 'Inter', sans-serif;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
        }}
        .title {{
            font-size: 3rem;
            font-weight: 900;
            background: linear-gradient(135deg, #7C3AED, #06B6D4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 20px;
        }}
        .subtitle {{
            font-size: 1.2rem;
            color: #CBD5E1;
            margin-bottom: 40px;
        }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .metric-card {{
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 30px;
            text-align: center;
        }}
        .metric-value {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 10px;
        }}
        .metric-label {{
            font-size: 1rem;
            color: #CBD5E1;
        }}
        .success {{ color: #10B981; }}
        .warning {{ color: #F59E0B; }}
        .danger {{ color: #EF4444; }}
        .cta {{
            text-align: center;
            margin-top: 40px;
        }}
        .cta-button {{
            background: linear-gradient(135deg, #7C3AED, #06B6D4);
            color: white;
            padding: 15px 30px;
            border-radius: 12px;
            text-decoration: none;
            font-weight: 600;
            display: inline-block;
            transition: all 0.3s ease;
        }}
        .cta-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(124, 58, 237, 0.4);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">AI Fitness Coach App</h1>
            <p class="subtitle">Demo Analysis Results</p>
        </div>
        
        <div class="metrics">
            <div class="metric-card">
                <div class="metric-value success">85%</div>
                <div class="metric-label">Market Demand</div>
            </div>
            <div class="metric-card">
                <div class="metric-value warning">60%</div>
                <div class="metric-label">Competition</div>
            </div>
            <div class="metric-card">
                <div class="metric-value success">78%</div>
                <div class="metric-label">Success Probability</div>
            </div>
            <div class="metric-card">
                <div class="metric-value success">8.2/10</div>
                <div class="metric-label">Feasibility Score</div>
            </div>
        </div>
        
        <div class="cta">
            <a href="/login" class="cta-button">
                <i class="fas fa-arrow-left"></i>
                Back to Login
            </a>
        </div>
    </div>
</body>
</html>
        '''

def run_server():
    """Run the simple HTTP server"""
    port = 8000
    host = '0.0.0.0'
    
    try:
        server = HTTPServer((host, port), CustomHandler)
        print(f"🚀 AI Business Idea Validator Server Running!")
        print(f"📍 Address: http://localhost:{port}/")
        print(f"📍 Address: http://127.0.0.1:{port}/")
        print(f"🔐 Login: username='demo', password='demo123'")
        print(f"🎯 Demo: http://localhost:{port}/demo")
        print(f"🛑 Press Ctrl+C to stop server")
        print("-" * 50)
        
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == '__main__':
    run_server()
