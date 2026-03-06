#!/usr/bin/env python3
"""
Freesound Downloader - interactive console for downloading sounds from freesound.org
Usage: python freesound_downloader.py
"""

import sys
import os
import webbrowser
import http.server
import socketserver
import urllib.parse
import json
import subprocess
import argparse
import asyncio
from pathlib import Path

PORT = 8765
# Cross-platform paths for cookie storage
SCRIPT_DIR = Path(__file__).parent
COOKIE_FILE = SCRIPT_DIR / ".freesound_cookies"
SESSION_FILE = SCRIPT_DIR / ".freesound_session.json"

class CookieHandler(http.server.SimpleHTTPRequestHandler):
    """Handler for receiving cookies via redirect"""
    
    def do_GET(self):
        if self.path.startswith('/callback'):
            # Get cookies from headers or URL parameters
            cookies = self.headers.get('Cookie', '')
            
            # If cookies in URL parameters (fallback)
            if not cookies and '?' in self.path:
                from urllib.parse import urlparse, parse_qs
                parsed = urlparse(self.path)
                params = parse_qs(parsed.query)
                cookie_parts = []
                for key in ['csrftoken', 'sessionid']:
                    if key in params and params[key]:
                        cookie_parts.append(f"{key}={params[key][0]}")
                if cookie_parts:
                    cookies = '; '.join(cookie_parts)
            
            if cookies:
                # Save cookies
                with open(COOKIE_FILE, 'w') as f:
                    f.write(cookies)
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                
                html = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Cookies received!</title>
                    <meta charset="utf-8">
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            height: 100vh;
                            margin: 0;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                        }
                        .container {
                            text-align: center;
                            background: rgba(0,0,0,0.3);
                            padding: 40px;
                            border-radius: 20px;
                            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                        }
                        h1 { font-size: 48px; margin: 0 0 20px 0; }
                        p { font-size: 18px; margin: 10px 0; }
                        .success { color: #4ade80; font-weight: bold; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>✅ Success!</h1>
                        <p class="success">Cookies successfully received and saved!</p>
                        <p>You can close this window.</p>
                        <p style="font-size: 14px; opacity: 0.8;">File saved: {}</p>
                    </div>
                    <script>
                        setTimeout(() => window.close(), 3000);
                    </script>
                </body>
                </html>
                """.format(COOKIE_FILE)
                
                self.wfile.write(html.encode('utf-8'))
                
                # Signal to main process
                if hasattr(self.server, 'cookies_received'):
                    self.server.cookies_received = True
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'No cookies received')
        else:
            self.send_response(404)
            self.end_headers()

def start_server():
    """Start local server for receiving cookies"""
    handler = CookieHandler
    httpd = socketserver.TCPServer(("", PORT), handler)
    httpd.cookies_received = False
    return httpd

def get_cookies_interactive():
    """Interactive cookie acquisition"""
    print("🌐 Starting local server for cookie acquisition...")
    print(f"📡 Server listening on port {PORT}")
    print()
    
    httpd = start_server()
    
    # URL for redirect after authorization
    callback_url = f"http://localhost:{PORT}/callback"
    
    # Ask user which authentication method they prefer
    print("🔐 Authentication options:")
    print("   1. Manual in browser")
    print("   2. Enter login/password here (RECOMMENDED - most stable)")
    print()
    try:
        choice = input("Choose option (1/2, Enter=2): ").strip() or "2"
    except (EOFError, KeyboardInterrupt):
        choice = "2"  # Default to option 2 (most stable)
    
    if choice == "2":
        # Automatic authentication via requests
        username = input("Login (email): ").strip()
        password = input("Password: ").strip()
        
        print("\n🔐 Authenticating...")
        import urllib.request
        import urllib.parse
        
        # Get CSRF token
        login_url = "https://freesound.org/home/login/"
        req = urllib.request.Request(login_url)
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            import re
            csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', html)
            if not csrf_match:
                print("❌ Failed to get CSRF token")
                return False
            csrf_token = csrf_match.group(1)
        
        # Submit login form
        data = urllib.parse.urlencode({
            'username': username,
            'password': password,
            'csrfmiddlewaretoken': csrf_token,
            'next': callback_url
        }).encode('utf-8')
        
        req = urllib.request.Request(login_url, data=data)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        req.add_header('Referer', login_url)
        
        # Create cookie jar
        import http.cookiejar
        cookie_jar = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
        
        try:
            response = opener.open(req)
            response_html = response.read().decode('utf-8')
            final_url = response.geturl()
            
            # Check if authentication was successful
            # If redirect to home or has post-login elements
            is_success = (
                final_url != login_url or  # Redirect after successful login
                'logout' in response_html or  # Logout button
                '/home/' in final_url or  # Redirect to home
                'My sounds' in response_html  # Profile element
            )
            
            if is_success:
                # Save cookies
                cookies = []
                for cookie in cookie_jar:
                    if cookie.name in ['csrftoken', 'sessionid']:
                        cookies.append(f"{cookie.name}={cookie.value}")
                
                if cookies:
                    with open(COOKIE_FILE, 'w') as f:
                        f.write('; '.join(cookies))
                    print(f"✅ Cookies saved to: {COOKIE_FILE}")
                    print(f"📋 Received cookies: csrftoken and sessionid")
                    return True
                else:
                    print("❌ Failed to get cookies from cookie jar")
                    print("💡 Try option 1 (manual in browser)")
                    return False
            else:
                # Check for error messages
                if 'error' in response_html.lower() or 'invalid' in response_html.lower():
                    print("❌ Authentication error. Check login/password")
                else:
                    print("❌ Authentication failed. Site structure may have changed")
                    print("💡 Try option 1 (manual in browser)")
                return False
        except urllib.error.HTTPError as e:
            print(f"❌ HTTP error: {e.code} - {e.reason}")
            if e.code == 403:
                print("💡 CAPTCHA may be required. Try option 1")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            print("💡 Try option 1 (manual in browser)")
            return False
    else:
        # Manual in browser
        print("🔓 Opening browser...")
        print("📝 Instructions:")
        print("   1. Enter login and password on freesound.org page")
        print("   2. After authentication press F12 (Developer Tools)")
        print("   3. Go to Console tab")
        print("   4. Copy and paste this code:")
        print()
        print("─" * 60)
        bookmarklet_code = f"""
// Copy this code to browser console (F12 -> Console) on freesound.org after authentication:
const cookies = document.cookie;
const params = new URLSearchParams();
cookies.split(';').forEach(c => {{
    const [name, value] = c.trim().split('=');
    if (name === 'csrftoken' || name === 'sessionid') {{
        params.append(name, value);
    }}
}});
window.open('{callback_url}?' + params.toString(), '_blank');
"""
        print(bookmarklet_code.strip())
        print("─" * 60)
        print()
        print("   5. OR simply navigate to this link (cookies will be in URL):")
        print(f"      {callback_url}")
        print()
        print("⏳ Waiting for cookies...")
        print("   (Press Ctrl+C to cancel)")
        print()
        
        # Open freesound.org
        webbrowser.open("https://freesound.org/home/login/")
    
    # Wait for cookies (max 5 minutes)
    httpd.timeout = 300
    try:
        while not httpd.cookies_received:
            httpd.handle_request()
    except KeyboardInterrupt:
        print("\n❌ Cancelled by user")
        httpd.server_close()
        return False
    
    httpd.server_close()
    
    if os.path.exists(COOKIE_FILE):
        print(f"✅ Cookies saved to: {COOKIE_FILE}")
        return True
    else:
        print("❌ Failed to receive cookies")
        return False

def check_cookies_valid(cookies_string):
    """Check if cookies are valid (attempt to get profile)"""
    if not cookies_string:
        return False
    
    try:
        import urllib.request
        import urllib.error
        
        req = urllib.request.Request("https://freesound.org/home/")
        req.add_header('Cookie', cookies_string)
        req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36')
        req.add_header('Referer', 'https://freesound.org/')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')
            final_url = response.geturl()
            
            # Check multiple signs of successful authentication
            is_valid = (
                'logout' in html.lower() or 
                'my sounds' in html.lower() or 
                '/home/' in final_url or
                'user-menu' in html.lower() or
                'account' in html.lower()
            )
            return is_valid
    except urllib.error.HTTPError as e:
        # 403 or 401 means cookies are invalid
        if e.code in [401, 403]:
            return False
        # Other errors may be temporary
        return False
    except Exception as e:
        # Other errors (timeout, network) - consider cookies valid
        # to avoid asking for authentication during temporary issues
        return True  # Conservative approach - consider valid

async def ensure_authenticated():
    """Check cookies and automatically authenticate if needed"""
    session_file = SESSION_FILE
    cookies_dict = None
    cookies_string = None
    
    # Load saved cookies
    if session_file.exists():
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                cookies_dict = json.load(f)
                cookie_parts = [
                    f"{name}={value}" 
                    for name, value in cookies_dict.items() 
                    if name in ['csrftoken', 'sessionid']
                ]
                if cookie_parts:
                    cookies_string = '; '.join(cookie_parts)
                    print(f"📁 Loaded saved cookies from {session_file}")
        except Exception as e:
            print(f"⚠️  Error loading cookies: {e}")
    
    # If no JSON, use old format
    if not cookies_string and os.path.exists(COOKIE_FILE):
        with open(COOKIE_FILE, 'r') as f:
            cookies_string = f.read().strip()
    
    # Check validity
    if cookies_string:
        print("🔍 Checking saved cookies...")
        if check_cookies_valid(cookies_string):
            print("✅ Authentication active (using saved cookies)")
            return cookies_string
        else:
            print("⚠️  Saved cookies expired or invalid")
    
    # Cookies invalid or missing - need authentication
    print("🔐 Authentication required...")
    print()
    
    # Use nodriver for authentication
    try:
        import nodriver as uc
    except ImportError:
        print("❌ nodriver not installed")
        print("   Install: pip install nodriver")
        print("   OR use: python freesound_downloader.py --get-cookies")
        return None
    
    print("🌐 Starting browser for authentication...")
    print()
    
    try:
        browser = await uc.start(headless=False)
        page = await browser.get('https://freesound.org/home/login/')
        
        print("="*60)
        print("📝 Enter login and password in browser")
        print("   Script will automatically detect authentication")
        print("="*60)
        print()
        print("⏳ Waiting for authentication...")
        
        max_wait = 300
        waited = 0
        
        while waited < max_wait:
            await asyncio.sleep(2)
            waited += 2
            
            try:
                current_url = page.url
                cookies = await browser.cookies.get_all()
                has_session = any(c.name == 'sessionid' for c in cookies)
                has_csrf = any(c.name == 'csrftoken' for c in cookies)
                
                if has_session and has_csrf and 'login' not in current_url:
                    print("\n✅ Authentication detected!")
                    break
                    
                if waited % 10 == 0:
                    print(f"   Waiting... ({waited}s)")
            except:
                await asyncio.sleep(2)
        
        if waited >= max_wait:
            print("\n❌ Timeout exceeded")
            try:
                browser.stop()
            except:
                pass
            return None
        
        # Get cookies
        raw_cookies = await browser.cookies.get_all()
        cookies_dict = {c.name: c.value for c in raw_cookies}
        
        # Close browser
        print("🔒 Closing browser...")
        try:
            browser.stop()
        except:
            pass
        
        # Save cookies
        cookie_parts = [
            f"{name}={value}" 
            for name, value in cookies_dict.items() 
            if name in ['csrftoken', 'sessionid']
        ]
        cookies_string = '; '.join(cookie_parts)
        
        # Save to files (cross-platform)
        try:
            COOKIE_FILE.parent.mkdir(parents=True, exist_ok=True)
            SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
            
            with open(COOKIE_FILE, 'w', encoding='utf-8') as f:
                f.write(cookies_string)
            with open(SESSION_FILE, 'w', encoding='utf-8') as f:
                json.dump(cookies_dict, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Cookies saved to: {SESSION_FILE}")
            return cookies_string
        except Exception as e:
            print(f"⚠️  Error saving cookies: {e}")
            # Still return cookies even if save failed
            return cookies_string
        
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

async def download_sound_async(sound_id, output_dir="downloads", sound_url=None):
    """Download sound from Freesound (async version)"""
    # Automatically check and get cookies if needed
    cookies = await ensure_authenticated()
    
    if not cookies:
        print("❌ Failed to get cookies")
        return False
    
    print(f"🔍 Getting sound information {sound_id}...")
    
    # Form URL - use provided or standard format
    if sound_url:
        # If full URL provided, use it
        page_url = sound_url
    else:
        # Try to find sound via API or standard format
        # First try via /sounds/{id}/
        page_url = f"https://freesound.org/sounds/{sound_id}/"
    
    # Get sound information
    import urllib.request
    req = urllib.request.Request(page_url)
    req.add_header('Cookie', cookies)
    req.add_header('User-Agent', 'Mozilla/5.0')
    req.add_header('Referer', 'https://freesound.org/')
    
    try:
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            response_url = response.geturl()
            
            # Check if redirected to login (session expired)
            if 'login' in response_url.lower() or ('login' in html.lower()[:1000] and 'logout' not in html.lower()):
                print("⚠️  Session expired. Re-authenticating...")
                # Clear invalid cookies
                if os.path.exists(COOKIE_FILE):
                    os.remove(COOKIE_FILE)
                if os.path.exists(SESSION_FILE):
                    os.remove(SESSION_FILE)
                # Re-authenticate
                cookies = await ensure_authenticated()
                if not cookies:
                    return False
                # Retry with new cookies
                req = urllib.request.Request(page_url)
                req.add_header('Cookie', cookies)
                req.add_header('User-Agent', 'Mozilla/5.0')
                req.add_header('Referer', 'https://freesound.org/')
                response = urllib.request.urlopen(req)
                html = response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"❌ Sound {sound_id} not found.")
            print(f"   Check if the URL is correct: {page_url}")
            print(f"   Example valid URL: https://freesound.org/people/troyane/sounds/233770/")
        elif e.code in [401, 403]:
            print("⚠️  Authentication failed. Session may have expired.")
            # Clear cookies and re-authenticate
            if os.path.exists(COOKIE_FILE):
                os.remove(COOKIE_FILE)
            if os.path.exists(SESSION_FILE):
                os.remove(SESSION_FILE)
            cookies = await ensure_authenticated()
            if cookies:
                print("✅ Re-authenticated. Please try downloading again.")
            return False
        else:
            print(f"❌ HTTP error {e.code}: {e.reason}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Find download link
    import re
    download_match = re.search(r'href="([^"]*download[^"]*)"', html)
    
    if not download_match:
        print("❌ Failed to find download link")
        print("   Possible reasons:")
        print("   - Sound requires login (session may have expired)")
        print("   - Sound is not available for download")
        print("   - Invalid URL or sound ID")
        print(f"   Check URL: {page_url}")
        print(f"   Example valid URL: https://freesound.org/people/troyane/sounds/233770/")
        return False
    
    download_url = download_match.group(1)
    if not download_url.startswith('http'):
        download_url = f"https://freesound.org{download_url}"
    
    # Extract filename
    filename_match = re.search(r'([^/]+\.(wav|mp3|ogg|flac))', download_url)
    if filename_match:
        filename = filename_match.group(1)
    else:
        filename = f"sound_{sound_id}.wav"
    
    # Create directory
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    
    print(f"⬇️  Downloading: {filename}")
    
    # Download file
    req = urllib.request.Request(download_url)
    req.add_header('Cookie', cookies)
    req.add_header('User-Agent', 'Mozilla/5.0')
    req.add_header('Referer', page_url)
    
    try:
        with urllib.request.urlopen(req) as response:
            with open(output_path, 'wb') as f:
                f.write(response.read())
        
        file_size = os.path.getsize(output_path)
        print(f"✅ Successfully downloaded: {output_path} ({file_size} bytes)")
        return True
    except Exception as e:
        print(f"❌ Download error: {e}")
        return False

def download_sound(sound_id, output_dir="downloads"):
    """Download sound from Freesound (synchronous wrapper)"""
    return asyncio.run(download_sound_async(sound_id, output_dir))

def extract_sound_id_from_url(url):
    """Extract sound_id from freesound.org URL"""
    import re
    # Formats: /people/username/sounds/12345/ or /sounds/12345/
    match = re.search(r'/sounds/(\d+)/?', url)
    if match:
        return int(match.group(1))
    return None

async def interactive_console(output_dir="downloads"):
    """Interactive console for downloading sounds"""
    try:
        from prompt_toolkit import PromptSession
        from prompt_toolkit.history import FileHistory
        from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
        from rich.console import Console
        from rich.panel import Panel
    except ImportError:
        print("❌ Required packages not installed: pip install prompt-toolkit rich")
        return
    
    console = Console()
    history_file = SCRIPT_DIR / ".freesound_history"
    session = PromptSession(
        history=FileHistory(str(history_file)),
        auto_suggest=AutoSuggestFromHistory(),
    )
    
    # Check authentication
    cookies = await ensure_authenticated()
    if not cookies:
        console.print("[red]❌ Failed to authenticate[/red]")
        return
    
    console.print(Panel.fit(
        "[bold green]✅ Authentication successful![/bold green]\n"
        "[yellow]Enter URL or sound ID to download[/yellow]\n"
        "[dim]Commands: help, exit, clear[/dim]",
        title="🎵 Freesound Downloader",
        border_style="green"
    ))
    console.print()
    console.print("[cyan]💡 Example URL:[/cyan] [dim]https://freesound.org/people/troyane/sounds/233770/[/dim]")
    console.print()
    console.print("[cyan]💡 Example URL:[/cyan] [dim]https://freesound.org/people/troyane/sounds/233770/[/dim]")
    console.print()
    
    loop = asyncio.get_event_loop()
    
    while True:
        try:
            # Use prompt in executor to avoid blocking event loop
            user_input = await loop.run_in_executor(None, lambda: session.prompt("🎵 > "))
            user_input = user_input.strip()
            
            if not user_input:
                continue
            
            # Commands
            if user_input.lower() in ['exit', 'quit', 'q']:
                console.print("[yellow]👋 Goodbye![/yellow]")
                break
            
            if user_input.lower() == 'clear':
                console.clear()
                continue
            
            if user_input.lower() == 'help':
                console.print(Panel(
                    "[bold]Available commands:[/bold]\n\n"
                    "[cyan]• URL or sound ID[/cyan] - download sound\n"
                    "  Examples:\n"
                    "  - https://freesound.org/people/user/sounds/12345/\n"
                    "  - 12345\n\n"
                    "[cyan]• help[/cyan] - show this help\n"
                    "[cyan]• exit / quit[/cyan] - exit\n"
                    "[cyan]• clear[/cyan] - clear screen",
                    title="📖 Help",
                    border_style="cyan"
                ))
                continue
            
            # Try to extract sound_id
            sound_id = None
            
            # If it's a number - it's an ID
            try:
                sound_id = int(user_input)
            except ValueError:
                # If it's a URL - extract ID
                if 'freesound.org' in user_input or '/sounds/' in user_input:
                    sound_id = extract_sound_id_from_url(user_input)
            
            if not sound_id:
                console.print(f"[red]❌ Failed to recognize sound ID: {user_input}[/red]")
                console.print("[yellow]💡 Enter URL or numeric sound ID[/yellow]")
                console.print("[dim]Example URL: https://freesound.org/people/troyane/sounds/233770/[/dim]")
                continue
            
            # Download sound
            console.print(f"[cyan]🔍 Downloading sound {sound_id}...[/cyan]")
            # Pass original URL if it was entered
            original_url = user_input if ('freesound.org' in user_input or '/sounds/' in user_input) else None
            success = await download_sound_async(sound_id, output_dir, original_url)
            
            if success:
                console.print(f"[green]✅ Done![/green]")
            else:
                console.print(f"[red]❌ Download error[/red]")
            
            console.print()
            
        except KeyboardInterrupt:
            console.print("\n[yellow]👋 Goodbye![/yellow]")
            break
        except EOFError:
            break
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")

def main():
    parser = argparse.ArgumentParser(
        description="Freesound Downloader - interactive console for downloading sounds from freesound.org",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start interactive console
  python freesound_downloader.py

  # Start with custom output directory
  python freesound_downloader.py --output ./my_sounds
        """
    )
    
    parser.add_argument('--output', '-o', default='downloads',
                       help='Output directory (default: downloads)')
    
    args = parser.parse_args()
    
    # Always start interactive console
    asyncio.run(interactive_console(args.output))

if __name__ == "__main__":
    main()
