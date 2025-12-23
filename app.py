from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
from datetime import datetime
from flask_cors import CORS
from flask_mail import Mail, Message
from flask_pymongo import PyMongo
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
# --- KONFIGURASI UPLOAD ---
# Folder tempat menyimpan gambar
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Pastikan folder upload ada saat aplikasi dijalankan
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    """Cek apakah ekstensi file diizinkan"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file_storage):
    if file_storage and allowed_file(file_storage.filename):
        filename = secure_filename(file_storage.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file_storage.save(file_path)
        
        # Samakan dengan format sertifikat yang bekerja
        return f"/static/uploads/{filename}" 
    return None

# --- KONFIGURASI KEAMANAN ---
# Secret Key wajib untuk session login & flash messages
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'kunci_rahasia_default_ganti_di_env')
CORS(app)

# --- KONFIGURASI MONGODB ---
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
mongo = PyMongo(app)

# --- KONFIGURASI EMAIL (PRODUCTION FIXED) ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
# Pastikan mengambil nilai langsung dari env dan hapus spasi yang mungkin terbawa
app.config['MAIL_USERNAME'] = str(os.getenv('MAIL_USERNAME', 'jonathanpys8@gmail.com')).strip()
app.config['MAIL_PASSWORD'] = str(os.getenv('MAIL_PASSWORD', 'evabxjwjqcycqfjy')).strip()
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']

mail = Mail(app)

# --- KONFIGURASI LOGIN MANAGER ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Jika belum login, redirect ke sini

# Class User Sederhana
class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    # Cek apakah user sesuai dengan yang di .env
    admin_user = os.getenv('ADMIN_USER', 'admin') # Default user: admin
    if user_id == admin_user:
        return User(user_id)
    return None

# --- DATA PORTFOLIO DEFAULT (FALLBACK) ---
# Data ini digunakan untuk seeding atau jika database error
portfolio_data = {
    "name": "Jonathan Pradipta Yudya Sulistyo",
    "title": "Information Systems Student & Full-Stack Developer",
    "location": "Surakarta, Indonesia",
    "email": "jonathanpys8@gmail.com",
    "phone": "+62 813 2626 0461",
    "bio": "A passionate Information Systems student with expertise in full-stack development, UI/UX design, and database management. Currently maintaining a 3.94 GPA while actively contributing to various tech projects and organizations.",
    "stats": {
        "projects": 12,
        "certificates": 3,
        "experience": "3+"
    },
    "social": {
        "linkedin": "https://www.linkedin.com/in/jonathanpys",
        "github": "https://github.com/jonathanpys",
        "portfolio": "https://jonathanpys.github.io",
        "instagram": "https://instagram.com/jonathanpys",
        "tiktok": "https://tiktok.com/@jonathanpys",
        "discord": "jonathanpys#0000"
    },
    "projects": [
        {
            "title": "E-Commerce Platform",
            "description": "Full-stack e-commerce solution with Laravel and MySQL",
            "technologies": ["Laravel", "MySQL", "Bootstrap"],
            "image": "https://images.unsplash.com/photo-1557821552-17105176677c?w=600&h=400&fit=crop"
        },
        {
            "title": "UI/UX Design Portfolio",
            "description": "Award-winning UI/UX designs using Figma",
            "technologies": ["Figma", "Adobe XD", "Prototyping"],
            "image": "https://images.unsplash.com/photo-1561070791-2526d30994b5?w=600&h=400&fit=crop"
        },
        {
            "title": "Database Management System",
            "description": "Oracle PL/SQL database solutions for enterprise",
            "technologies": ["Oracle", "PL/SQL", "Database Design"],
            "image": "https://images.unsplash.com/photo-1544383835-bda2bc66a55d?w=600&h=400&fit=crop"
        },
        {
            "title": "Social Media Content Creation",
            "description": "Video and graphic content for brand marketing",
            "technologies": ["Premiere Pro", "After Effects", "Photoshop"],
            "image": "https://images.unsplash.com/photo-1611162616305-c69b3fa7fbe0?w=600&h=400&fit=crop"
        },
        {
            "title": "Business Process Analysis Tool",
            "description": "Power BI dashboards for business insights",
            "technologies": ["Power BI", "Excel", "Data Analysis"],
            "image": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600&h=400&fit=crop"
        },
        {
            "title": "Web Development Projects",
            "description": "Multiple websites using PHP and modern frameworks",
            "technologies": ["PHP", "CodeIgniter", "HTML/CSS"],
            "image": "https://images.unsplash.com/photo-1547658719-da2b51169166?w=600&h=400&fit=crop"
        }
    ],
    "certificates": [
        {
            "title": "Database Programming with PL/SQL",
            "issuer": "Oracle Academy",
            "date": "July 2025",
            "image": "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=600&h=400&fit=crop"
        },
        {
            "title": "Database Design & Programming with SQL",
            "issuer": "Oracle Academy",
            "date": "December 2024",
            "image": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=600&h=400&fit=crop"
        },
        {
            "title": "Computer Programming Assistant (KKNI Level II)",
            "issuer": "Badan Nasional Sertifikasi Profesi (BNSP)",
            "date": "December 2022 - December 2025",
            "image": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=600&h=400&fit=crop"
        }
    ],
    "tools": [
        {"name": "Python", "category": "Backend"},
        {"name": "PHP", "category": "Backend"},
        {"name": "Laravel", "category": "Framework"},
        {"name": "CodeIgniter", "category": "Framework"},
        {"name": "Flask", "category": "Framework"},
        {"name": "HTML/CSS", "category": "Frontend"},
        {"name": "JavaScript", "category": "Frontend"},
        {"name": "MySQL", "category": "Database"},
        {"name": "MongoDB", "category": "Database"},
        {"name": "Oracle Database", "category": "Database"},
        {"name": "Figma", "category": "Design"},
        {"name": "Adobe Photoshop", "category": "Design"},
        {"name": "Adobe Premiere Pro", "category": "Design"},
        {"name": "Adobe After Effects", "category": "Design"},
        {"name": "CorelDRAW", "category": "Design"},
        {"name": "Canva", "category": "Design"},
        {"name": "Power BI", "category": "Analytics"},
        {"name": "Git", "category": "Tools"},
        {"name": "Excel", "category": "Tools"}
    ],
    "achievements": [
        {
            "title": "3rd Place Winner - UI/UX Competition",
            "event": "Information System Festival (ISFEST) 2024",
            "location": "Salatiga",
            "date": "September 2024",
            "description": "Awarded for excellence in UI/UX design using Figma in a national-scale competition held by Universitas Kristen Satya Wacana."
        }
    ],
    "experience": [
        {
            "title": "Social Media Marketing Intern",
            "company": "Semesta Group",
            "location": "Sukoharjo",
            "period": "July 2022 - September 2022",
            "responsibilities": [
                "Produced promotional and TikTok videos to strengthen the brand's social media presence",
                "Used graphic design and video editing tools such as Adobe Photoshop, Premiere Pro, Vegas Pro, and CorelDRAW",
                "Operated camera equipment for professional videography and photography needs",
                "Collaborated with the creative team to develop visual content across multiple brand accounts"
            ]
        },
        {
            "title": "Web Designer Intern",
            "company": "Semesta Group",
            "location": "Sukoharjo",
            "period": "February 2022 - April 2022",
            "responsibilities": [
                "Designed and developed websites for several brands within the Semesta Group portfolio",
                "Implemented web solutions using programming languages and frameworks such as PHP native, Laravel, and CodeIgniter",
                "Ensured functional and aesthetic web design standards were met using HTML and other web development tools"
            ]
        }
    ],
    "organizational": [
        {
            "title": "Staff of PIXEL Division",
            "organization": "Himpunan Mahasiswa Prodi Sistem Informasi (HMPSI)",
            "location": "Salatiga",
            "period": "January 2025 - December 2025",
            "responsibilities": [
                "Created high-quality video content for organizational publications using CapCut PC, Adobe Premiere Pro, and Adobe After Effects",
                "Designed professional promotional posters for various departmental events, utilizing Canva to enhance visual branding",
                "Served as a Videographer to capture and produce creative media content for the organization's social media platforms",
                "Collaborated within the PIXEL division to manage and execute digital asset requirements for the Information Systems student body"
            ]
        },
        {
            "title": "Committee Member of Event Creative Division",
            "organization": "ORACLESCAPE 2025",
            "location": "Salatiga",
            "period": "June 2025",
            "responsibilities": [
                "Formulated a comprehensive event rundown to ensure the structured execution of both seminar and workshop sessions",
                "Authored professional scripts for Master of Ceremonies (MC) and actively served as the MC for the workshop segment",
                "Acted as a Timekeeper during the seminar to maintain schedule precision and manage speaker transitions effectively",
                "Applied event management skills to coordinate creative elements, ensuring a seamless experience for all participants"
            ]
        },
        {
            "title": "Committee Member of Publication, Design, and Documentation Division",
            "organization": "PURE: SEMINAR & COMPETITION 2024",
            "location": "Salatiga",
            "period": "September 2024 - October 2024",
            "responsibilities": [
                "Contributed as a committee member for the PURE 2024 event organized by Satya Wacana Christian University",
                "Responsible for creating visual assets and promotional designs to support the publication of the seminar and competition",
                "Managed event documentation and ensured all design requirements for the Publication, Design, and Documentation division were met",
                "Collaborated with the committee team to ensure the successful execution of the event's branding and media presence"
            ]
        }
    ]
}

# --- HELPER FUNCTION ---
def get_db_data():
    """Mengambil data dari DB, jika gagal/kosong pakai default"""
    try:
        if mongo.db.portfolio.count_documents({}) > 0:
            data = mongo.db.portfolio.find_one({"name": portfolio_data["name"]})
            if data:
                return data
    except Exception as e:
        print(f"Database Warning: {e}")
    
    # Return default hardcoded data
    return portfolio_data

# --- PUBLIC ROUTES ---

@app.route('/')
def index():
    user_data = get_db_data()
    
    # --- LOGIKA OTOMATIS YEARS EXPERIENCE ---
    # Agar saat ini hasilnya "2", kita set Start Year = 2023.
    # Rumus: Tahun Sekarang (2025) - 2023 = 2 Tahun.
    # Nanti saat 1 Jan 2026, otomatis jadi: 2026 - 2023 = 3 Tahun.
    start_year = 2023 
    current_year = datetime.now().year
    
    # Hitung durasi
    experience_years = current_year - start_year
    
    # Masukkan hasil hitungan ke dalam data sebelum dikirim ke HTML
    # Ini akan menimpa data 'experience' yang ada di database sementara waktu
    if user_data and 'stats' in user_data:
        user_data['stats']['experience'] = f"{experience_years}+"
    
    return render_template('index.html', data=user_data)

@app.route('/seed-db')
def seed_database():
    try:
        existing_data = mongo.db.portfolio.find_one({"name": portfolio_data["name"]})
        if existing_data:
            return jsonify({"message": "Data sudah ada di MongoDB Atlas! Tidak perlu upload ulang."})
        
        mongo.db.portfolio.insert_one(portfolio_data)
        return jsonify({"message": "Berhasil! Data portfolio_data telah di-upload ke MongoDB Atlas."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/contact', methods=['POST'])
def contact():
    try:
        data = request.get_json()
        name = data.get('name')
        email_pengunjung = data.get('email')
        message_content = data.get('message')
        
        msg = Message(
            subject=f"Pesan Baru Portfolio dari: {name}",
            recipients=['jonathanpys8@gmail.com'] # Email Anda
        )
        msg.body = f"""
        Halo Jonathan, ada pesan baru:
        
        Nama: {name}
        Email: {email_pengunjung}
        
        Pesan:
        {message_content}
        """
        mail.send(msg)
        return jsonify({"success": True, "message": "Pesan terkirim!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

# --- ADMIN / CMS ROUTES ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Ambil kredensial admin dari .env (atau default admin/admin123)
        env_user = os.getenv('ADMIN_USER', 'admin')
        env_pass = os.getenv('ADMIN_PASS', 'admin123')
        
        if username == env_user and password == env_pass:
            user = User(username)
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Username atau Password Salah!')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/admin')
@login_required
def admin_dashboard():
    data = get_db_data()
    return render_template('admin.html', data=data)

# 1. Update Profile Logic
@app.route('/admin/update_profile', methods=['POST'])
@login_required
def update_profile():
    try:
        mongo.db.portfolio.update_one(
            {"name": portfolio_data["name"]},
            {"$set": {
                "title": request.form.get('title'),
                "bio": request.form.get('bio'),
                "social.linkedin": request.form.get('linkedin'),
                "social.github": request.form.get('github'),
                "social.instagram": request.form.get('instagram')
            }}
        )
        flash('Profile updated successfully!', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'danger')
    return redirect(url_for('admin_dashboard'))

# UPDATE ROUTE ADD PROJECT
@app.route('/admin/add_project', methods=['POST'])
@login_required
def add_project():
    try:
        # 1. Ambil file gambar
        image_file = request.files.get('image')
        image_path = None
        
        # 2. Simpan gambar jika ada (pastikan return-nya 'uploads/filename.jpg')
        if image_file and image_file.filename != '':
            image_path = save_uploaded_file(image_file)
        
        # 3. Susun data project baru
        # Pastikan 'image' mendapatkan variabel image_path yang baru saja diproses
        new_project = {
            "title": request.form.get('title'),
            "description": request.form.get('description'),
            "image": image_path,  # Ini krusial: harus variabel image_path
            "video": request.form.get('video'),
            "link": request.form.get('link'),  # <--- Input Link baru
            "technologies": [tech.strip() for tech in request.form.get('technologies').split(',')]
        }
        
        # 4. Update ke MongoDB
        mongo.db.portfolio.update_one(
            {"name": portfolio_data["name"]},
            {"$push": {"projects": new_project}}
        )
        flash('Project added successfully!', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'danger')
    return redirect(url_for('admin_dashboard'))

# 3. Delete Project Logic
@app.route('/admin/delete_project', methods=['POST'])
@login_required
def delete_project():
    try:
        title_to_delete = request.form.get('title')
        mongo.db.portfolio.update_one(
            {"name": portfolio_data["name"]},
            {"$pull": {"projects": {"title": title_to_delete}}}
        )
        flash('Project deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'danger')
    return redirect(url_for('admin_dashboard'))

# UPDATE ROUTE ADD CERTIFICATE
@app.route('/admin/add_certificate', methods=['POST'])
@login_required
def add_certificate():
    try:
        # 1. Ambil file dari form
        image_file = request.files.get('image')
        
        # 2. Proses Upload
        image_path = save_uploaded_file(image_file)
        
        if not image_path:
            flash('Error: Image required or format not allowed', 'warning')
            return redirect(url_for('admin_dashboard'))

        new_cert = {
            "title": request.form.get('title'),
            "issuer": request.form.get('issuer'),
            "date": request.form.get('date'),
            "image": image_path # Simpan path file
        }
        
        mongo.db.portfolio.update_one(
            {"name": portfolio_data["name"]},
            {"$push": {"certificates": new_cert}}
        )
        flash('Certificate added successfully!', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'danger')
    return redirect(url_for('admin_dashboard'))

# 5. Delete Certificate Logic
@app.route('/admin/delete_certificate', methods=['POST'])
@login_required
def delete_certificate():
    try:
        title_to_delete = request.form.get('title')
        mongo.db.portfolio.update_one(
            {"name": portfolio_data["name"]},
            {"$pull": {"certificates": {"title": title_to_delete}}}
        )
        flash('Certificate deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'danger')
    return redirect(url_for('admin_dashboard'))

# 6. Add Achievement
@app.route('/admin/add_achievement', methods=['POST'])
@login_required
def add_achievement():
    try:
        new_achievement = {
            "title": request.form.get('title'),
            "event": request.form.get('event'),
            "location": request.form.get('location'),
            "date": request.form.get('date'),
            "description": request.form.get('description')
        }
        
        mongo.db.portfolio.update_one(
            {"name": portfolio_data["name"]},
            {"$push": {"achievements": new_achievement}}
        )
        flash('Achievement added successfully!', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'danger')
    return redirect(url_for('admin_dashboard'))

# 7. Delete Achievement
@app.route('/admin/delete_achievement', methods=['POST'])
@login_required
def delete_achievement():
    try:
        title_to_delete = request.form.get('title')
        mongo.db.portfolio.update_one(
            {"name": portfolio_data["name"]},
            {"$pull": {"achievements": {"title": title_to_delete}}}
        )
        flash('Achievement deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'danger')
    return redirect(url_for('admin_dashboard'))


# --- LOGIC UNTUK EXPERIENCE ---

# 8. Add Experience
@app.route('/admin/add_experience', methods=['POST'])
@login_required
def add_experience():
    try:
        # Mengambil responsibilities dan memisahkan berdasarkan baris baru (Enter)
        resp_text = request.form.get('responsibilities')
        # Split by newline dan hapus spasi kosong
        resp_list = [r.strip() for r in resp_text.split('\n') if r.strip()]

        new_experience = {
            "title": request.form.get('title'),
            "company": request.form.get('company'),
            "location": request.form.get('location'),
            "period": request.form.get('period'),
            "responsibilities": resp_list
        }
        
        mongo.db.portfolio.update_one(
            {"name": portfolio_data["name"]},
            {"$push": {"experience": new_experience}}
        )
        flash('Experience added successfully!', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'danger')
    return redirect(url_for('admin_dashboard'))

# 9. Delete Experience
@app.route('/admin/delete_experience', methods=['POST'])
@login_required
def delete_experience():
    try:
        title_to_delete = request.form.get('title')
        # Kita gunakan kombinasi title dan company agar lebih spesifik (opsional, title saja juga bisa)
        mongo.db.portfolio.update_one(
            {"name": portfolio_data["name"]},
            {"$pull": {"experience": {"title": title_to_delete}}}
        )
        flash('Experience deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'danger')
    return redirect(url_for('admin_dashboard'))

# --- LOGIC UNTUK ORGANIZATION ---

# 10. Add Organization
@app.route('/admin/add_organization', methods=['POST'])
@login_required
def add_organization():
    try:
        # Mengambil responsibilities dan memisahkan berdasarkan baris baru (Enter)
        resp_text = request.form.get('responsibilities')
        resp_list = [r.strip() for r in resp_text.split('\n') if r.strip()]

        new_org = {
            "title": request.form.get('title'),
            "organization": request.form.get('organization'),
            "location": request.form.get('location'),
            "period": request.form.get('period'),
            "responsibilities": resp_list
        }
        
        mongo.db.portfolio.update_one(
            {"name": portfolio_data["name"]},
            {"$push": {"organizational": new_org}}
        )
        flash('Organization added successfully!', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'danger')
    return redirect(url_for('admin_dashboard'))

# 11. Delete Organization
@app.route('/admin/delete_organization', methods=['POST'])
@login_required
def delete_organization():
    try:
        title_to_delete = request.form.get('title')
        mongo.db.portfolio.update_one(
            {"name": portfolio_data["name"]},
            {"$pull": {"organizational": {"title": title_to_delete}}}
        )
        flash('Organization deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'danger')
    return redirect(url_for('admin_dashboard'))

# --- LOGIC UNTUK SOCIAL LINKS (CONTACT) ---

# 12. Add Social Link
@app.route('/admin/add_social', methods=['POST'])
@login_required
def add_social():
    try:
        new_social = {
            "platform": request.form.get('platform'), # Contoh: WhatsApp
            "url": request.form.get('url'),           # Contoh: https://wa.me/628...
            "icon": request.form.get('icon'),         # Contoh: fab fa-whatsapp
            "color": request.form.get('color')        # Contoh: bg-green-500
        }
        
        mongo.db.portfolio.update_one(
            {"name": portfolio_data["name"]},
            {"$push": {"social_links": new_social}}
        )
        flash('Social link added successfully!', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'danger')
    return redirect(url_for('admin_dashboard'))

# 13. Delete Social Link
@app.route('/admin/delete_social', methods=['POST'])
@login_required
def delete_social():
    try:
        platform_to_delete = request.form.get('platform')
        mongo.db.portfolio.update_one(
            {"name": portfolio_data["name"]},
            {"$pull": {"social_links": {"platform": platform_to_delete}}}
        )
        flash('Social link deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'danger')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)