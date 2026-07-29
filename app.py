from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
import csv
import io
import os
from datetime import datetime, timedelta
from openpyxl import Workbook, load_workbook

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

CORS(app)

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'zaojiatong.db')


# ==================== 数据库 ====================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    # 用户表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            company TEXT DEFAULT '',
            phone TEXT DEFAULT '',
            role TEXT DEFAULT 'user',
            created_at TEXT DEFAULT (datetime('now','localtime'))
        )
    """)

    # 项目表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            region TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # 材料查询记录表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            project_id INTEGER,
            material_name TEXT NOT NULL,
            spec TEXT DEFAULT '',
            unit TEXT DEFAULT '',
            region TEXT DEFAULT '',
            price TEXT DEFAULT '',
            price_unit TEXT DEFAULT '',
            source TEXT DEFAULT '',
            note TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)

    # 检查有没有默认管理员，没有则创建
    admin = cur.execute("SELECT id FROM users WHERE username='admin'").fetchone()
    if not admin:
        cur.execute(
            "INSERT INTO users (username, password_hash, company, role) VALUES (?, ?, ?, ?)",
            ('admin', generate_password_hash('admin123'), '中联永信工程管理', 'admin')
        )

    conn.commit()
    conn.close()


# ==================== 登录装饰器 ====================

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "请先登录", "code": "NO_AUTH"}), 401
        return f(*args, **kwargs)
    return decorated


# ==================== 页面路由 ====================

@app.route("/")
def index():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template("index.html")


@app.route("/login")
def login_page():
    return render_template("login.html")


@app.route("/register")
def register_page():
    return render_template("register.html")


# ==================== API：用户 ====================

@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json()
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()
    company = (data.get("company") or "").strip()

    if not username or not password:
        return jsonify({"error": "用户名和密码不能为空"}), 400
    if len(username) < 2:
        return jsonify({"error": "用户名至少2个字符"}), 400
    if len(password) < 6:
        return jsonify({"error": "密码至少6位"}), 400

    db = get_db()
    exist = db.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
    if exist:
        db.close()
        return jsonify({"error": "用户名已存在"}), 400

    db.execute(
        "INSERT INTO users (username, password_hash, company) VALUES (?, ?, ?)",
        (username, generate_password_hash(password), company)
    )
    db.commit()
    db.close()

    return jsonify({"message": "注册成功，请登录"})


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()

    if not username or not password:
        return jsonify({"error": "请输入用户名和密码"}), 400

    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    db.close()

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "用户名或密码错误"}), 401

    session['user_id'] = user["id"]
    session['username'] = user["username"]
    session['company'] = user["company"]
    session['role'] = user["role"]
    session.permanent = True

    return jsonify({
        "message": "登录成功",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "company": user["company"],
            "role": user["role"]
        }
    })


@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"message": "已退出"})


@app.route("/api/me", methods=["GET"])
@login_required
def api_me():
    db = get_db()
    user = db.execute("SELECT id, username, company, role, created_at FROM users WHERE id=?", (session['user_id'],)).fetchone()
    db.close()
    if not user:
        return jsonify({"error": "用户不存在"}), 404
    return jsonify(dict(user))


# ==================== API：项目 ====================

@app.route("/api/projects", methods=["GET"])
@login_required
def api_projects():
    db = get_db()
    rows = db.execute(
        "SELECT * FROM projects WHERE user_id=? ORDER BY created_at DESC",
        (session['user_id'],)
    ).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/projects", methods=["POST"])
@login_required
def api_create_project():
    data = request.get_json()
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "项目名称不能为空"}), 400

    db = get_db()
    cur = db.execute(
        "INSERT INTO projects (user_id, name, description, region) VALUES (?, ?, ?, ?)",
        (session['user_id'], name, data.get("description", ""), data.get("region", ""))
    )
    db.commit()
    pid = cur.lastrowid
    db.close()

    return jsonify({"id": pid, "message": "项目创建成功"})


@app.route("/api/projects/<int:pid>", methods=["DELETE"])
@login_required
def api_delete_project(pid):
    db = get_db()
    db.execute("DELETE FROM projects WHERE id=? AND user_id=?", (pid, session['user_id']))
    db.commit()
    db.close()
    return jsonify({"message": "已删除"})


# ==================== API：材料查询 ====================

@app.route("/api/search", methods=["POST"])
@login_required
def search():
    data = request.get_json()
    keyword = (data.get("keyword") or "").strip()
    region = (data.get("region") or "").strip()
    project_id = data.get("project_id")

    if not keyword:
        return jsonify({"error": "请输入材料名称"}), 400

    results = search_price(keyword, region)
    save_query(keyword, "", "", region, results, project_id)

    return jsonify({"keyword": keyword, "region": region, "results": results})


@app.route("/api/batch", methods=["POST"])
@login_required
def batch():
    if "file" not in request.files:
        return jsonify({"error": "请上传文件"}), 400

    file = request.files["file"]
    filename = file.filename.lower()

    try:
        if filename.endswith(".csv"):
            rows = parse_csv(file)
        elif filename.endswith((".xlsx", ".xls")):
            rows = parse_excel(file)
        else:
            return jsonify({"error": "仅支持 .csv / .xlsx / .xls 格式"}), 400
    except Exception as e:
        return jsonify({"error": f"文件解析失败: {str(e)}"}), 400

    if not rows:
        return jsonify({"error": "文件中没有数据"}), 400

    region = request.form.get("region", "").strip()
    project_id = request.form.get("project_id")

    all_results = []
    for i, row in enumerate(rows):
        name = str(row[0]).strip() if len(row) > 0 and row[0] else ""
        spec = str(row[1]).strip() if len(row) > 1 and row[1] else ""
        unit = str(row[2]).strip() if len(row) > 2 and row[2] else ""
        if not name:
            continue
        kw = f"{name} {spec}".strip()
        results = search_price(kw, region)
        save_query(name, spec, unit, region, results, project_id)
        all_results.append({
            "seq": i + 1,
            "name": name,
            "spec": spec,
            "unit": unit,
            "keyword": kw,
            "results": results
        })

    return jsonify({"total": len(all_results), "items": all_results})


@app.route("/api/export", methods=["POST"])
@login_required
def export():
    data = request.get_json()
    items = data.get("items", [])
    project_id = data.get("project_id")

    # 如果有 project_id，从数据库读取该项目所有查询
    if project_id:
        db = get_db()
        rows = db.execute(
            "SELECT * FROM queries WHERE user_id=? AND project_id=? ORDER BY created_at",
            (session['user_id'], project_id)
        ).fetchall()
        db.close()
        items = export_from_db(rows)
    elif not items:
        return jsonify({"error": "没有数据可导出"}), 400

    wb = Workbook()
    ws = wb.active
    ws.title = "材料价格查询结果"
    ws.append(["序号", "材料名称", "规格型号", "单位", "查询地区",
               "参考价格", "价格单位", "信息来源", "备注", "查询时间"])

    for i, item in enumerate(items):
        results = item.get("results", [])
        if results:
            for r in results:
                ws.append([
                    i + 1,
                    item.get("name", ""),
                    item.get("spec", ""),
                    item.get("unit", ""),
                    item.get("region", ""),
                    r.get("price", ""),
                    r.get("unit", ""),
                    r.get("source", ""),
                    r.get("note", ""),
                    datetime.now().strftime("%Y-%m-%d %H:%M")
                ])
        else:
            ws.append([
                i + 1,
                item.get("name", ""),
                item.get("spec", ""),
                item.get("unit", ""),
                item.get("region", ""),
                "未查到", "", "", "",
                datetime.now().strftime("%Y-%m-%d %H:%M")
            ])

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=f"材料价格查询_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    )


@app.route("/api/history", methods=["GET"])
@login_required
def history():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    project_id = request.args.get("project_id")

    db = get_db()
    where = "WHERE user_id=?"
    params = [session['user_id']]
    if project_id:
        where += " AND project_id=?"
        params.append(project_id)

    total = db.execute(f"SELECT COUNT(*) FROM queries {where}", params).fetchone()[0]
    rows = db.execute(
        f"SELECT * FROM queries {where} ORDER BY created_at DESC LIMIT ? OFFSET ?",
        params + [per_page, (page - 1) * per_page]
    ).fetchall()
    db.close()

    return jsonify({
        "total": total,
        "page": page,
        "per_page": per_page,
        "items": [dict(r) for r in rows]
    })


# ==================== 核心：搜索 + 存库 ====================

def save_query(name, spec, unit, region, results, project_id=None):
    """保存查询记录到数据库"""
    db = get_db()
    pid = project_id if project_id else None
    if results:
        for r in results:
            db.execute(
                """INSERT INTO queries (user_id, project_id, material_name, spec, unit, region,
                   price, price_unit, source, note) VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (session['user_id'], pid, name, spec, unit, region,
                 r.get("price", ""), r.get("unit", ""),
                 r.get("source", ""), r.get("note", ""))
            )
    else:
        db.execute(
            """INSERT INTO queries (user_id, project_id, material_name, spec, unit, region)
               VALUES (?,?,?,?,?,?)""",
            (session['user_id'], pid, name, spec, unit, region)
        )
    db.commit()
    db.close()


def search_price(keyword, region=""):
    """搜索材料价格

    TODO: 替换为真实数据源
    - 方案1: 接入造价通 API (https://api.zjtcn.com/open/api/list)
    - 方案2: requests + BeautifulSoup 抓取造价通搜索页
    - 方案3: 接入 mysteel / 各地造价信息网 API
    - 方案4: 维护本地材料价格数据库
    """
    results = []

    # 示例数据，实际使用时替换
    kw_lower = keyword.lower()
    sample = {
        "c30混凝土": [{"price": "420", "unit": "元/m³", "source": "造价通", "note": "C30 商品砼 2026年7月", "region": region}],
        "c25混凝土": [{"price": "390", "unit": "元/m³", "source": "造价通", "note": "C25 商品砼 2026年7月", "region": region}],
        "c35混凝土": [{"price": "450", "unit": "元/m³", "source": "造价通", "note": "C35 商品砼 2026年7月", "region": region}],
        "hrb400螺纹钢": [{"price": "3850", "unit": "元/吨", "source": "Mysteel", "note": "HRB400 φ16-25", "region": region}],
        "hrb400e螺纹钢": [{"price": "3920", "unit": "元/吨", "source": "Mysteel", "note": "HRB400E φ16-25", "region": region}],
        "p.o42.5水泥": [{"price": "480", "unit": "元/吨", "source": "造价通", "note": "P.O 42.5 袋装", "region": region}],
        "p.o52.5水泥": [{"price": "550", "unit": "元/吨", "source": "造价通", "note": "P.O 52.5 袋装", "region": region}],
        "xps保温板": [{"price": "58", "unit": "元/m²", "source": "造价通", "note": "XPS 50mm B1级", "region": region}],
        "sbs防水卷材": [{"price": "32", "unit": "元/m²", "source": "造价通", "note": "SBS-II 3mm", "region": region}],
        "加气块": [{"price": "280", "unit": "元/m³", "source": "造价通", "note": "600×240×200 B06", "region": region}],
    }

    for k, v in sample.items():
        if k in kw_lower:
            results = v
            break

    return results


def export_from_db(rows):
    """将数据库记录转为导出格式"""
    groups = {}
    for r in rows:
        key = (r["material_name"], r["spec"], r["unit"])
        if key not in groups:
            groups[key] = {
                "name": r["material_name"],
                "spec": r["spec"],
                "unit": r["unit"],
                "region": r["region"],
                "results": []
            }
        if r["price"]:
            groups[key]["results"].append({
                "price": r["price"],
                "unit": r["price_unit"],
                "source": r["source"],
                "note": r["note"]
            })
    return list(groups.values())


# ==================== 文件解析 ====================

def parse_csv(file):
    content = file.read().decode("utf-8-sig")
    reader = csv.reader(io.StringIO(content))
    rows = []
    for i, row in enumerate(reader):
        if i == 0:
            continue
        if any(cell.strip() for cell in row if cell):
            rows.append(row)
    return rows


def parse_excel(file):
    wb = load_workbook(file, read_only=True)
    ws = wb.active
    rows = []
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i == 0:
            continue
        if any(str(c).strip() for c in row if c):
            rows.append(row)
    return rows


# ==================== 启动 ====================

if __name__ == "__main__":
    init_db()
    print("✅ 造价通材料价格查询系统已启动")
    print("   访问地址: http://127.0.0.1:5000")
    print("   默认管理员: admin / admin123")
    app.run(host="0.0.0.0", port=5000, debug=True)
