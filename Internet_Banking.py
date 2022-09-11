from asyncio.windows_events import NULL
import base64
import random
import time
from datetime import datetime, date
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:123@localhost:5432/Internet_Banking?sslmode=disable'
db = SQLAlchemy(app)

class Nasabah(db.Model):
    id_nasabah = db.Column(db.Integer, primary_key=True, index=True, nullable=False, unique=True) 
    nik = db.Column(db.String(50), nullable=False)
    nama = db.Column(db.String(50), nullable=False)
    no_hp = db.Column(db.String(50), nullable=False)
    pekerjaan = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    
class Cabang(db.Model):
    id_cabang = db.Column(db.Integer, primary_key=True, index=True, nullable=False, unique=True) 
    regional = db.Column(db.String(50), nullable=False)
    nama = db.Column(db.String(50), nullable=False)
    alamat = db.Column(db.String(250), nullable=False)
    kota = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    

class Account(db.Model): 
    id_account = db.Column(db.Integer, primary_key=True, index=True, nullable=False, unique=True) 
    no_rekening = db.Column(db.String(50), nullable=False)
    saldo = db.Column(db.Integer, nullable=True)                                            
    status = db.Column(db.String(50), nullable=True)
    jenis = db.Column(db.String(50), nullable=True)    
    id_nasabah = db.Column(db.Integer, db.ForeignKey('nasabah.id_nasabah'), nullable=True)
    id_cabang = db.Column(db.Integer, db.ForeignKey('cabang.id_cabang'), nullable=True)
    last_update = db.Column (db.DateTime, nullable=False)
    # transakasi_rel = db.relationship('Transaksi', backref='account')                                    #menghubungkan tabel akun dan transaksi, karena akan ada operasi antar saldo dan kolom tiap transaksi 
    
class Transaksi(db.Model):
    id_transaksi = db.Column(db.Integer, primary_key=True, index=True, nullable=False, unique=True)
    waktu = db.Column (db.DateTime, nullable=False)                                                     # untuk mencatat waktu tiap melakukan transaksi
    saldo_masuk = db.Column(db.Integer, nullable=True)
    saldo_keluar = db.Column(db.Integer, nullable=True)                                                # merujuk saldo pada akun                       
    jenis_transaksi = db.Column(db.String(50), nullable=True)
    id_pengirim = db.Column(db.Integer, db.ForeignKey('account.id_account'), nullable=True)                               
    id_penerima = db.Column(db.Integer, db.ForeignKey('account.id_account'), nullable=True)
    
db.create_all() 
db.session.commit()


def auth_nasabah(auth):
    encode = base64.b64decode(auth[6:])
    str_encode = encode.decode('ascii')
    lst = str_encode.split(':')
    username = lst[0]
    password = lst[1]   
    nasabah = Nasabah.query.filter_by(username=username).filter_by(password=password).first()
    if nasabah:
        return (nasabah.id_nasabah)
    else:
        return 
    

def auth_cabang(auth):
    encode = base64.b64decode(auth[6:])
    str_encode = encode.decode('ascii')
    lst = str_encode.split(':')
    username = lst[0]
    password = lst[1]   
    cabang = Cabang.query.filter_by(username=username).filter_by(password=password).first()
    if cabang:
        return (cabang.id_cabang)
    else:
        return 0

# ----------------------------------------------------------------------------------------------->>> HOME (pingin buat login user or adm)
@app.route('/nasabah') 
def home_nasabah():
    return jsonify(
        "Selamat Datang di Bank Alltale"
    )


@app.route('/admin') 
def home_admin():
    return jsonify(
        "Selamat Datang di Bank Alltale"
    )


# ----------------------------------------------------------------------------------------------->>> NASABAH
@app.route('/nasabah/register', methods=['POST'])#by user
def create_nasabah():
    data = request.get_json()
    n = Nasabah( 
        nik = data['nik'],
        nama = data['nama'],
        no_hp = data['no_hp'],
        pekerjaan = data['pekerjaan'],
        username = data['username'],
        email = data['email'],
        password = data['password']
	)
    try:                                    
        db.session.add(n)
        db.session.commit()
    except:
        return {
            "pesan": "data gagal tersimpan"
        }, 400   
    return {
        "pesan": "data tersimpan"
    }, 201

@app.route('/cabang/nasabah', methods=['GET']) #by admin 
def get_():
    decode = request.headers.get('Authorization')
    allow = auth_cabang(decode)
    # cabang = Cabang.query.filter_by(id_cabang=allow).filter_by(id_).first()
    if not allow :
            return {
                    "pesan" : "akses ditolak !!"
                }, 400
    else:
        
        nasabah_ = db.engine.execute(f"select id_nasabah from account where id_cabang = {allow} group by id_nasabah")
        arr = []
        for i in nasabah_:
            a = Nasabah.query.filter_by(id_nasabah=i.id_nasabah).first()
            arr.append({
                'nama' : a.nama,
                'email' : a.email
            })
        return jsonify(arr)
       
@app.route('/nasabah/update', methods=['PUT'])#by user
def update_nasabah():
    decode = request.headers.get('Authorization')
    allow = auth_nasabah(decode)
    nasabah = Nasabah.query.filter_by(id_nasabah=allow).first()
    if not nasabah :
        return {
            'pesan': 'data gagal tersimpan'
        }, 400
    else:   
        data  = request.get_json()
        nasabah.nik = data['nik']
        nasabah.nama = data['nama']
        nasabah.no_hp = data['no_hp']
        nasabah.pekerjaan = data['pekerjaan']
        nasabah.username = data['username']
        nasabah.email = data['email']
        nasabah.password = data['password']
        db.session.commit()
        return {
            "pesan": "data telah tersimpan"
            }, 201



# ----------------------------------------------------------------------------------------------->>> CABANG
@app.route('/cabang/register', methods=['POST']) #by admin
def create_cabang():
    data = request.get_json()
    c = Cabang( 
        
        regional = data['regional'],
        nama = data['nama'],
        alamat = data['alamat'],
        kota = data['kota'],
        username = data['username'],
        email = data['email'],
        password = data['password']
	)
    try:                                    
        db.session.add(c)
        db.session.commit()
    except:
        return {
            "pesan": "data tidak tersimpan"
        }, 400   
    return {
        "pesan": "data tersimpan"
    }, 201

@app.route('/cabang/profile', methods=['GET']) #by admin
def get_cabang_login():
    decode = request.headers.get('Authorization')
    allow = auth_cabang(decode)
    cabang = Cabang.query.filter_by(id_cabang=allow).first()
    if not allow :
        return {
                "pesan" : "akses ditolak !!"
            }, 400
    else:
        return jsonify([{
                "regional" : cabang.regional,
                "nama" : cabang.nama,
                "alamat" : cabang.alamat,
                "kota" : cabang.kota
            }]), 201
        
@app.route('/cabang/update', methods=['PUT']) #by admin
def update_cabang():
    decode = request.headers.get('Authorization')
    allow = auth_nasabah(decode)
    cabang = Cabang.query.filter_by(id_cabang=allow).first()
    if not cabang :
        return {
            'pesan': 'data gagal tersimpan'
        }, 400
    else:
        data  = request.get_json()
        cabang = Cabang.query.filter_by(id_cabang=id).first()
        cabang.regional = data['regional']
        cabang.nama = data['nama']
        cabang.alamat = data['alamat']
        cabang.kota = data['kota']
        return {
            "pesan": "data telah tersimpan"
            }, 201

@app.route('/cabang/total', methods=['GET'])
def jumlah_account():
    decode = request.headers.get('Authorization')
    allow = auth_cabang(decode)
    cabang = Cabang.query.filter_by(id_cabang=allow).first()
    if not cabang :
        return {
            'pesan': 'Akses Ditolak !!'
        }, 400
    else:
        total = db.engine.execute("select count(account.id_account), count(distinct(account.id_nasabah)), sum(account.saldo) from account inner join cabang on account.id_cabang = cabang.id_cabang")
        arr = []
        for i in total:
            arr.append (
                {
                    'total_account' : i[0],
                    'total_nasabah' : i[1],
                    'Jumlah_saldo' : i[2]
                    
                }), 201
        return jsonify(arr)

@app.route('/cabang/total_percabang', methods=['GET'])
def jumlah_account_percabang():
    decode = request.headers.get('Authorization')
    allow = auth_cabang(decode)
    cabang = Cabang.query.filter_by(id_cabang=allow).first()
    if not cabang :
        return {
            'pesan': 'Akses Ditolak !!'
        }, 400
    else:
        total = db.engine.execute(f"select count(account.id_account), count(distinct(account.id_nasabah)), sum(account.saldo) from account inner join cabang on account.id_cabang = cabang.id_cabang where account.id_cabang = {allow}")
        arr = []
        for i in total:
            arr.append (
                {
                    'total_account' : i[0],
                    'total_nasabah' : i[1],
                    'Jumlah_saldo' : i[2]
                    
                }), 201
        return jsonify(arr)

@app.route('/cabang/transaksi_periode', methods=['GET'])
def jumlah_transaksi():
    decode = request.headers.get('Authorization')
    allow = auth_cabang(decode)
    cabang = Cabang.query.filter_by(id_cabang=allow).first()
    data = request.get_json()
    waktu_1 = data["waktu_1"]
    waktu_2 = datetime.now()
    # waktu_2 = time.mktime(datetime.strptime(a,"%Y-%m-%d").timetuple())
    if not cabang :
        return {
            'pesan': 'Akses Ditolak !!'
        }, 400
    else:
        total = db.engine.execute(f"select  b.masuk, a.keluar, c.periode from (select sum(transaksi.saldo_keluar) as keluar from transaksi inner join account on transaksi.id_pengirim = account.id_account  inner join cabang on account.id_cabang = cabang.id_cabang where account.id_cabang = 2)a,(select sum(transaksi.saldo_masuk) as masuk from transaksi inner join account on transaksi.id_penerima = account.id_account  inner join cabang on account.id_cabang = cabang.id_cabang where account.id_cabang = 2)b, (select transaksi.waktu as periode from transaksi inner join account on transaksi.id_penerima = account.id_account  inner join cabang on account.id_cabang = cabang.id_cabang where waktu BETWEEN '2022-09-01' AND '{waktu_2}')c")
        arr = []
        for i in total:
            arr.append (
                {
                    'total_masuk' : i[0],
                    'total_keluar' : i[1],
                    'periode' : i[2]
                }), 201
        return jsonify(arr)



# ----------------------------------------------------------------------------------------------->>> ACCOUNT
@app.route('/create_account_nasabah', methods=['POST']) #by admin 
def create_account():
    decode = request.headers.get('Authorization')
    allow = auth_cabang(decode)
    cabang = Cabang.query.filter_by(id_cabang=allow).first()
    if not cabang :
        return {
            'pesan': 'Akses Ditolak !!'
        }, 400
    else:
        data = request.get_json()
        a = Account( 
            no_rekening = random.randint(100000, 500000) + data["id_nasabah"],              #random.randint (u/ mengambil angka secara acak range dari 100000-500000) + data u/ menambahkan id agar tidak sama 
            saldo = data['saldo'],
            status = "aktif",                                                               #awal membuat akun
            jenis = data['jenis'],
            id_nasabah = data['id_nasabah'],
            id_cabang = data['id_cabang'],
            last_update = datetime.now()                                                    # fungsi mengambil waktu saat itu
        )
                                    
        db.session.add(a)                                                                   # menambah data ke column
        db.session.commit()                                                                 # menambah data ke database
        acc = db.engine.execute("select * from account order by id_account  DESC limit 1")  # select data mysql
        # new_account = []
        # for x in  acc:                                                                       
        #     new_account.append({'id_account': x[0], 'no_rekening': x[1], 'saldo' : x[2], 'status' : x[3], 'last_update': x[4], 'id_nasabah' : x[5], 'id_cabang' : x[6]}),201 
        # return new_account
        ### yang diatas untuk looping apabila lebih dari satu tabel contohnya join
        for x in  acc:                                                                      # looping data dalam baris pada tabel akun (tidak ditambah list kosong karena hanya satu tabel 
            return({'id_account': x[0], 'no_rekening': x[1], 'saldo' : x[2], 'status' : x[3], 'last_update': x[4], 'jenis' : x[5], 'id_nasabah' : x[6], 'id_cabang' : x[7]}),201 # untuk menampilkan baris baru yang ditambahkan pada tabel akun 
   
@app.route('/account/profile/', methods=['GET']) #by user
def get_account():
    decode = request.headers.get('Authorization')
    nasabah_id = auth_nasabah(decode)                               #auth dari nasabah
    accounts = Account.query.filter_by(id_nasabah=nasabah_id).all() #merujuk pada username dan password nasabah
    arr = []
    arr2 = []
    for i in accounts :
        arr.append(i.no_rekening)
    for j in arr :
        dorman = Account.query.filter_by(no_rekening=j).first()
        days_off = datetime.now() - dorman.last_update
        if days_off.days > 90 :
            arr2.append({'id_account' : dorman.id_account,
            "saldo" : dorman.saldo,
            "status" : "Tidak Aktif",
            "jenis" : dorman.jenis,
            'id_nasabah' : dorman.id_nasabah
            })
            dorman.status = "tidak aktif"                           #untuk update di db
        else:
            arr2.append({'id_account' : dorman.id_account,
            "saldo" : dorman.saldo,
            "status" : "Aktif",
            'id_nasabah' : dorman.id_nasabah
            })
    db.session.commit()                  
    return arr2 
                                             
@app.route('/account/deactivate/<id>', methods=['PUT']) #by admin
def deactivate_account(id):
    decode = request.headers.get('Authorization')
    cabang = auth_cabang(decode)
    if cabang :
        account_id = Account.query.filter_by(id_account=id).first()
        if account_id :
            account_id.status = "tidak aktif"
        db.session.commit()  
        return { 
            "pesan" : "akun anda telah non aktif"
        },201
    return { 
            "pesan" : "password atau username anda salah"
        },400
    
@app.route('/account/reactivate/<id>', methods=['PUT']) 
def reactivate_account(id):
    decode = request.headers.get('Authorization')
    cabang = auth_cabang(decode)
    if cabang :
        account_id = Account.query.filter_by(id_account=id).first()
        if account_id :
            account_id.status = "aktif"
        db.session.commit()  
        return { 
            "pesan" : "akun anda telah aktif"
        },201
    return { 
            "pesan" : "password atau username anda salah"
        },400    
    


# ----------------------------------------------------------------------------------------------->>> TRANSAKSI
@app.route('/transaksi/transfer', methods=['POST']) #by user
def transaksi_transfer():
    decode = request.headers.get('Authorization')
    id_nasabah = auth_nasabah(decode)
    if id_nasabah :
        data = request.get_json()
        pengirim = Account.query.filter_by(id_account=data['id_pengirim']).filter_by(id_nasabah=id_nasabah).first() 
        if not pengirim :
            return {
                    "pesan" : "akses ditolak !!"
                }, 400
        penerima = Account.query.filter_by(id_account=data['id_penerima']).first() 
        day_off = datetime.now() - pengirim.last_update
        no_activity = day_off.days   
        if no_activity > 90 :
            pengirim.status == "Tidak Aktif"
            return {
                    "pesan" : "akun anda tidak aktif"
                }, 400
        else :
            if pengirim.jenis == "PLATINUM":
                if data['saldo_keluar'] <= 25000000:
                    if pengirim.saldo - data['saldo_keluar'] > 50000 :
                        pengirim.saldo = pengirim.saldo - data['saldo_keluar']
                        pengirim.last_update == datetime.now()
                        saldosebelum = pengirim.saldo + data['saldo_keluar']
                        t = Transaksi( 
                            waktu = datetime.now(),
                            saldo_masuk = data['saldo_keluar'],
                            saldo_keluar = data['saldo_keluar'],
                            jenis_transaksi = "Transfer",
                            id_pengirim = data['id_pengirim'],              
                            id_penerima = data['id_penerima']               
                                    )
                        penerima.saldo = penerima.saldo + data['saldo_keluar']
                        db.session.add(t)
                        db.session.commit()
                        return { 
                            "waktu" : datetime.now(),
                            "saldo_sebelum" : saldosebelum,
                            "saldo_setelah" : pengirim.saldo,                                                    
                            "transfer" : data['saldo_keluar']
                        }, 201
                    else:
                        return {
                            "pesan": "saldo anda tidak cukup"
                        }, 400
                else:
                    return {
                            "pesan": "anda melebihi maksimum"
                        }, 400
                        
            if pengirim.jenis == "GOLD":
                if data['saldo_keluar'] <= 50000000:
                    if pengirim.saldo - data['saldo_keluar'] > 50000 :
                        pengirim.saldo = pengirim.saldo - data['saldo_keluar']
                        pengirim.last_update == datetime.now()
                        saldosebelum = pengirim.saldo + data['saldo_keluar']
                        t = Transaksi( 
                            waktu = datetime.now(),
                            saldo_masuk = data['saldo_keluar'],
                            saldo_keluar = data['saldo_keluar'],
                            jenis_transaksi = "Transfer",
                            id_pengirim = data['id_pengirim'],              
                            id_penerima = data['id_penerima']               
                                    )
                        penerima.saldo = penerima.saldo + data['saldo_keluar']
                        db.session.add(t)
                        db.session.commit()
                        return { 
                            "waktu" : datetime.now(),
                            "saldo_sebelum" : saldosebelum,
                            "saldo_setelah" : pengirim.saldo,                                                    
                            "transfer" : data['saldo_keluar']
                        }, 201
                    else:
                        return {
                            "pesan": "saldo anda tidak cukup"
                        }, 400
                else:
                    return {
                            "pesan": "anda melebihi maksimum"
                        }, 400

            if pengirim.jenis == "BLACK":
                if data['saldo_keluar'] <= 100000000:
                    if pengirim.saldo - data['saldo_keluar'] > 50000 :
                        pengirim.saldo = pengirim.saldo - data['saldo_keluar']
                        pengirim.last_update == datetime.now()
                        saldosebelum = pengirim.saldo + data['saldo_keluar']
                        t = Transaksi( 
                            waktu = datetime.now(),
                            saldo_masuk = data['saldo_keluar'],
                            saldo_keluar = data['saldo_keluar'],
                            jenis_transaksi = "Transfer",
                            id_pengirim = data['id_pengirim'],              
                            id_penerima = data['id_penerima']               
                                    )
                        penerima.saldo = penerima.saldo + data['saldo_keluar'] 
                        db.session.add(t)
                        db.session.commit()
                        return { 
                            "waktu" : datetime.now(),
                            "saldo_sebelum" : saldosebelum,
                            "saldo_setelah" : pengirim.saldo,                                                    
                            "transfer" : data['saldo_keluar']
                        }, 201
                    else:
                        return {
                            "pesan": "saldo anda tidak cukup"
                        }, 400
                else:
                    return {
                            "pesan": "anda melebihi maksimum"
                        }, 400                  
    else :
        return {
            'pesan': 'Akses Ditolak !!'
        }, 400

@app.route('/cabang/transaksi/setor_tunai', methods=['POST']) #by admin
def transaksi_setor_tunai():
    decode = request.headers.get('Authorization')
    allow = auth_cabang(decode)
    cabang = Cabang.query.filter_by(id_cabang=allow).first()
    if not cabang :
        return {
            'pesan': 'Akses Ditolak !!'
        }, 400
    else:
        data = request.get_json()
        penerima = Account.query.filter_by(id_account=data['id_penerima']).first()
        day_off = datetime.now() - penerima.last_update
        no_activity = day_off.days   
        if no_activity > 90 :
            penerima.status == "Tidak Aktif"
            return {
                    "pesan" : "akun tidak aktif"
                }, 400
        else:
            penerima.last_update == datetime.now()
            # saldosebelum = penerima.saldo - data['saldo_masuk']
            t = Transaksi( 
                waktu = datetime.now(),
                saldo_masuk = data['saldo_masuk'],
                saldo_keluar = 0,
                jenis_transaksi = "Setor Tunai",
                id_pengirim = data['id_penerima'],              
                id_penerima = data['id_penerima']               
                )
            penerima.saldo = penerima.saldo + data['saldo_masuk']
            db.session.add(t)
            db.session.commit()
            return { 
                "waktu" : datetime.now(),
                "setor_tunai" : data['saldo_masuk'],
                # "saldo_sebelum" : saldosebelum,                                                    
                "saldo_sesudah" : penerima.saldo
            }, 201

@app.route('/transaksi/debit', methods=['POST']) #by user #mirip seperti transfer
def transaksi_debit():
    decode = request.headers.get('Authorization')
    id_nasabah = auth_nasabah(decode)
    if id_nasabah :
        data = request.get_json()
        pengirim = Account.query.filter_by(id_account=data['id_pengirim']).filter_by(id_nasabah=id_nasabah).first() 
        if not pengirim :
            return {
                    "pesan" : "akses ditolak !!"
                }, 400       #query di postman 
        day_off = datetime.now() - pengirim.last_update
        no_activity = day_off.days   
        if no_activity > 90 :
            pengirim.status == "Tidak Aktif"
            return {
                    "pesan" : "akun anda tidak aktif"
                }, 400
        else :
            if pengirim.saldo - data['saldo_keluar'] > 50000 :
                pengirim.saldo = pengirim.saldo - data['saldo_keluar']
                pengirim.last_update == datetime.now()
                saldosebelum = pengirim.saldo + data['saldo_keluar']
                t = Transaksi( 
                    waktu = datetime.now(),
                    saldo_masuk = 0,
                    saldo_keluar = data['saldo_keluar'],
                    jenis_transaksi = "Debit",
                    id_pengirim = data['id_pengirim'],              
                    id_penerima = data['id_penerima']              
                        )
                db.session.add(t)
                db.session.commit()
                return { 
                    "waktu" : datetime.now(),
                    "saldo_sebelum" : saldosebelum,
                    "saldo_setelah" : pengirim.saldo,                                                    
                    "debit" : data['saldo_keluar']
                }, 201
            else:
                return {
                    "pesan": "saldo anda tidak cukup"
                }, 400
    else :
        return {
            'pesan': 'Akses Ditolak !!'
        }, 400

@app.route('/transaksi/tarik_tunai', methods=['POST']) #by user #mirip seperti transfer
def transaksi_tarik_tunai():
    decode = request.headers.get('Authorization')
    id_nasabah = auth_nasabah(decode)
    if id_nasabah :
        data = request.get_json()
        pengirim = Account.query.filter_by(id_account=data['id_pengirim']).filter_by(id_nasabah=id_nasabah).first() 
        if not pengirim :
            return {
                    "pesan" : "akses ditolak !!"
                }, 400        
        day_off = datetime.now() - pengirim.last_update
        no_activity = day_off.days   
        if no_activity > 90 :
            pengirim.status == "Tidak Aktif"
            return {
                    "pesan" : "akun anda tidak aktif"
                }, 400
        else :
            if pengirim.saldo - data['saldo_keluar'] > 50000 :
                pengirim.saldo = pengirim.saldo - data['saldo_keluar']
                pengirim.last_update == datetime.now()
                saldosebelum = pengirim.saldo + data['saldo_keluar']
                t = Transaksi( 
                    waktu = datetime.now(),
                    saldo_masuk = 0,
                    saldo_keluar = data['saldo_keluar'],
                    jenis_transaksi = "Tarik Tunai",
                    id_pengirim = data['id_pengirim'],              
                    # id_penerima = data['id_penerima']               
                        )
                db.session.add(t)
                db.session.commit()
                return { 
                    "waktu" : datetime.now(),
                    "saldo_sebelum" : saldosebelum,
                    "saldo_setelah" : pengirim.saldo,                                                    
                    "tarik_tunai" : data['saldo_keluar']
                }, 201
            else:
                return {
                    "pesan": "saldo anda tidak cukup"
                }, 400
    else :
        return {
            'pesan': 'Akses Ditolak !!'
        }, 400

@app.route('/transaksi/history', methods=['GET']) #by user
def get_transaksi():
    decode = request.headers.get('Authorization')
    id_nasabah = auth_nasabah(decode)
    if id_nasabah:                                          
        transaksi = Transaksi.query.all()
        arr = []
        for i in transaksi :
            # arr.append(i.id_transaksi)
        # for j in arr:
           arr.append( {
                    'waktu' : i.waktu,                                                    
                    'saldo_masuk' : i.saldo_masuk,
                    'saldo_keluar' : i.saldo_keluar,
                    'jenis_transaksi' : i.jenis_transaksi,
                    'id_pengirim' : i.id_pengirim,
                    'id_penerima' : i.id_penerima
                }  )
        return jsonify(arr),201
          
        # return {
        #     'pesan': arr
        # }, 400
    else :
        return {
            'pesan': 'Akses Ditolak !!'
        }, 400

    




