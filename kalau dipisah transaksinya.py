from asyncio.windows_events import NULL
import base64
import random
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
    last_update = db.Column (db.DateTime, nullable=False)
    jenis = db.Column(db.String(50), nullable=True)    
    id_nasabah = db.Column(db.Integer, db.ForeignKey('nasabah.id_nasabah'), nullable=True)
    id_cabang = db.Column(db.Integer, db.ForeignKey('cabang.id_cabang'), nullable=True)
    transakasi_rel = db.relationship('Transaksi', backref='account')                                    #menghubungkan tabel akun dan transaksi, karena akan ada operasi antar saldo dan kolom tiap transaksi 
    
class Transaksi(db.Model):
    id_transaksi = db.Column(db.Integer, primary_key=True, index=True, nullable=False, unique=True)
    id_account = db.Column(db.Integer, db.ForeignKey('account.id_account'), nullable=False)
    waktu = db.Column (db.DateTime, nullable=False)                                                     # untuk mencatat waktu tiap melakukan transaksi
    saldo = saldo = db.Column(db.Integer, nullable=True)                                                # merujuk saldo pada akun                       
    transfer_masuk = db.Column(db.Integer, nullable=True)
    setor_tunai = db.Column(db.Integer, nullable=True)                                                   
    transfer = db.Column(db.Integer, nullable=True) 
    debit = db.Column(db.Integer, nullable=True)
    kredit = db.Column(db.Integer, nullable=True)
    tarik_tunai = db.Column(db.Integer, nullable=True)
    saldo_masuk = db.Column(db.Integer, nullable=True)
    saldo_keluar = db.Column(db.Integer, nullable=True) 
    deposit_rel = db.relationship('Setor_Tunai', backref='transaksi')
    transfer_rel = db.relationship('Transfer', backref='transaksi')
    debit_rel = db.relationship('Debit', backref='transaksi')
    kredit_rel = db.relationship('Kredit', backref='transaksi')
    tarikk_tunai_rel = db.relationship('Tarik_Tunai', backref='transaksi')

class Setor_Tunai(db.Model):
    id_setor_tunai = db.Column(db.Integer, primary_key=True, index=True, nullable=False, unique=True)
    id_transaksi = db.Column(db.Integer, db.ForeignKey('transaksi.id_transaksi'), nullable=False)
    waktu = db.Column (db.DateTime, nullable=False)                                                     
    setor_tunai = db.Column(db.Integer, nullable=True)                                                   
    id_account = db.Column(db.Integer, db.ForeignKey('account.id_account'), nullable=False)                
    id_cabang = db.Column(db.Integer, db.ForeignKey('cabang.id_cabang'), nullable=True)                 #yang melakukan admin           

class Transfer(db.Model):
    id_transfer = db.Column(db.Integer, primary_key=True, index=True, nullable=False, unique=True)
    id_transaksi = db.Column(db.Integer, db.ForeignKey('transaksi.id_transaksi'), nullable=False)
    waktu = db.Column (db.DateTime, nullable=False)                                                     
    transfer = db.Column(db.Integer, nullable=True)                                                   
    id_account_pengirim = db.Column(db.Integer, db.ForeignKey('account.id_account'), nullable=False)                
    id_cabang_pengirim = db.Column(db.Integer, db.ForeignKey('cabang.id_cabang'), nullable=True)
    id_account_penerima = db.Column(db.Integer, db.ForeignKey('account.id_account'), nullable=False)                
    id_cabang_penerima = db.Column(db.Integer, db.ForeignKey('cabang.id_cabang'), nullable=True)

class Debit(db.Model):
    id_debit = db.Column(db.Integer, primary_key=True, index=True, nullable=False, unique=True)
    id_transaksi = db.Column(db.Integer, db.ForeignKey('transaksi.id_transaksi'), nullable=False)
    waktu = db.Column (db.DateTime, nullable=False)                                                     
    debit = db.Column(db.Integer, nullable=True)                                                   
    id_account = db.Column(db.Integer, db.ForeignKey('account.id_account'), nullable=False)               
    id_cabang = db.Column(db.Integer, db.ForeignKey('cabang.id_cabang'), nullable=True)                   

class Kredit(db.Model):
    id_debit = db.Column(db.Integer, primary_key=True, index=True, nullable=False, unique=True)
    id_transaksi = db.Column(db.Integer, db.ForeignKey('transaksi.id_transaksi'), nullable=False)
    waktu = db.Column (db.DateTime, nullable=False)                                                     
    kredit = db.Column(db.Integer, nullable=True)                                                   
    id_account = db.Column(db.Integer, db.ForeignKey('account.id_account'), nullable=False)               
    id_cabang = db.Column(db.Integer, db.ForeignKey('cabang.id_cabang'), nullable=True)

class Tarik_Tunai(db.Model):
    id_tarik_tunai = db.Column(db.Integer, primary_key=True, index=True, nullable=False, unique=True)
    id_transaksi = db.Column(db.Integer, db.ForeignKey('transaksi.id_transaksi'), nullable=False)
    waktu = db.Column (db.DateTime, nullable=False)                                                     
    tarik_tunai = db.Column(db.Integer, nullable=True)                                                   
    id_account = db.Column(db.Integer, db.ForeignKey('account.id_account'), nullable=False)               
    id_cabang = db.Column(db.Integer, db.ForeignKey('cabang.id_cabang'), nullable=True)

    

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
        return str(nasabah.id_nasabah)
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
@app.route('/') 
def home():
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
def get_nasabah():
    decode = request.headers.get('Authorization')
    allow = auth_cabang(decode)
    cabang = Cabang.query.filter_by(id_cabang=allow).first()
    if not cabang :
        return {
            'pesan': 'Akses Ditolak !!'
        }, 400
    else:
        return jsonify([
            {
                'nik' : nasabah.nik,
                'nama' : nasabah.nama,
                'no_hp' : nasabah.no_hp,
                'pekerjaan' : nasabah.pekerjaan,
                'username' : nasabah.username,
                'email' : nasabah.email,
                'password' : nasabah.password
            } for nasabah in Nasabah.query.all() 
        ]), 201

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



# ----------------------------------------------------------------------------------------------->>> ADMIN
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
    if not cabang :
        return {
            'pesan': 'Akses Ditolak !!'
        }, 400
    else:
        return jsonify([
            {
                'regional' : cabang.regional,
                'nama' : cabang.nama,
                'alamat' : cabang.alamat,
                'kota' : cabang.kota
            } for cabang in Cabang.query.all() 
        ]), 201

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

@app.route('/cabang/nasabah_setor_tunai', methods=['POST'])
def nasabah_setor_tunai():
    decode = request.headers.get('Authorization')
    allow = auth_cabang(decode)
    cabang = Cabang.query.filter_by(id_cabang=allow).first()
    if not cabang :
        return {
            'pesan': 'Akses Ditolak !!'
        }, 400
    else:
        data = request.get_json()
        # cabang_id = Cabang.query.filter_by(id_cabang=data['id_cabang']).first()       #query di postman
        # cabang_kota = Cabang.query.filter_by(kota=data['kota']).first()
        penerima = Account.query.filter_by(no_rekening=data['id_penerima']).first()
        transaksi_penerima = Transaksi.query.filter_by(id_transaksi=data['id_transaksi']).first()
        day_off = datetime.now() - penerima.last_update
        no_activity = day_off.days   
        if no_activity > 90 :
            penerima.status == "Tidak Aktif"
            return {
                    "pesan" : "akun tidak aktif"
                }, 400
        else:
            penerima.last_update == datetime.now()
            saldo_sebelum = penerima.saldo - data['setor_tunai']
            s = Setor_Tunai( 
                waktu = datetime.now(),                                                     
                setor_tunai = data['setor_tunai'],                                                   
                id_account = data['id_account'],                
                id_cabang = data['id_cabang']
                    )
            penerima.saldo = penerima.saldo + data['setor_tunai']
            transaksi_penerima.saldo_masuk += data['transfer']
            db.session.add(s)
            db.session.commit()
            return { 
                "waktu" : datetime.now(),
                "setor_tunai" : data['setor_tunai'],
                "saldo_sebelum" : saldo_sebelum,                                                    
                "saldo_sesudah" : penerima.saldo
            }, 201



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
            return({'id_account': x[0], 'no_rekening': x[1], 'saldo' : x[2], 'status' : x[3], 'jenis': x[4], 'last_update' : x[5], 'id_nasabah' : x[6], 'id_cabang' : x[7]}),201 # untuk menampilkan baris baru yang ditambahkan pada tabel akun 
   
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
def post_transaksi_transfer():
    decode = request.headers.get('Authorization')
    id_nasabah = auth_nasabah(decode)
    if id_nasabah :
        data = request.get_json()
        pengirim = Account.query.filter_by(id_account=data['id_account']).first()       #query di postman
        penerima = Account.query.filter_by(no_rekening=data['id_penerima']).first()
        transaksi_pengirim = Transaksi.query.filter_by(id_transaksi=data['id_transaksi']).first()
        transaksi_penerima = Transaksi.query.filter_by(id_transaksi=data['id_transaksi']).first()
        day_off = datetime.now() - pengirim.last_update
        no_activity = day_off.days   
        if no_activity > 90 :
            pengirim.status == "Tidak Aktif"
            return {
                    "pesan" : "akun anda tidak aktif"
                }, 400
        else :
            if pengirim.jenis == "PLATINUM":
                if data['transfer'] <= 25000000:
                    if pengirim.saldo - data['transfer'] > 50000 :
                        pengirim.saldo = pengirim.saldo - data['transfer']
                        pengirim.last_update == datetime.now()
                        saldo_sebelum = pengirim.saldo + data['transfer']
                        t = Transaksi( 
                            id_account = data['id_account'],
                            waktu = datetime.now(),
                            saldo = pengirim.saldo,                                                    
                            transfer_masuk = 0,
                            setor_tunai = 0,
                            transfer = data['transfer'],
                            debit = 0,
                            kredit = 0,
                            tarik_tunai = 0,
                            saldo_masuk = 0,
                            saldo_keluar = data['transfer']
                        )
                        t_ = Transfer(
                            waktu = datetime.now(),                                                     
                            transfer = data['transfer'],                                                   
                            id_account_pengirim = data['id_account'],               
                            id_cabang_pengirim = data['id_cabang'],
                            id_account_penerima = data['id_account'],                
                            id_cabang_penerima = data['id_cabang']
                        )
                        penerima.saldo = penerima.saldo + data['transfer']
                        transaksi_pengirim.saldo_masuk = 0
                        transaksi_pengirim.saldo_keluar = data['transfer']
                        transaksi_penerima.saldo_masuk += data['transfer']
                        transaksi_penerima.saldo_keluar = 0
                        db.session.add(t)
                        db.session.add(t_)
                        db.session.commit()
                        return { 
                            "waktu" : datetime.now(),
                            "saldo_sebelum" : saldo_sebelum,
                            "saldo_setelah" : pengirim.saldo,                                                    
                            "transfer" : data['transfer']
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
                if data['transfer'] <= 50000000:
                    if pengirim.saldo - data['transfer'] > 50000 :
                        pengirim.saldo = pengirim.saldo - data['transfer']
                        pengirim.last_update == datetime.now()
                        saldo_sebelum = pengirim.saldo + data['transfer']
                        t = Transaksi( 
                            id_account = data['id_account'],
                            waktu = datetime.now(),
                            saldo = pengirim.saldo,                                                    
                            transfer_masuk = 0,
                            setor_tunai = 0,
                            transfer = data['transfer'],
                            debit = 0,
                            kredit = 0,
                            tarik_tunai = 0,
                            saldo_masuk = 0,
                            saldo_keluar = data['transfer']
                        )
                        t_ = Transfer(
                            waktu = datetime.now(),                                                     
                            transfer = data['transfer'],                                                   
                            id_account_pengirim = data['id_account'],               
                            id_cabang_pengirim = data['id_cabang'],
                            id_account_penerima = data['id_account'],                
                            id_cabang_penerima = data['id_cabang']
                        )
                        penerima.saldo = penerima.saldo + data['transfer']
                        transaksi_pengirim.saldo_masuk = 0
                        transaksi_pengirim.saldo_keluar = data['transfer']
                        transaksi_penerima.saldo_masuk += data['transfer']
                        transaksi_penerima.saldo_keluar = 0
                        db.session.add(t)
                        db.session.add(t_)
                        db.session.commit()
                        return { 
                            "waktu" : datetime.now(),
                            "saldo_sebelum" : saldo_sebelum,
                            "saldo_setelah" : pengirim.saldo,                                                    
                            "transfer" : data['transfer']
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
                if data['transfer'] <= 100000000:
                    if pengirim.saldo - data['transfer'] > 50000 :
                        pengirim.saldo = pengirim.saldo - data['transfer']
                        pengirim.last_update == datetime.now()
                        saldo_sebelum = pengirim.saldo + data['transfer']
                        t = Transaksi( 
                            id_account = data['id_account'],
                            waktu = datetime.now(),
                            saldo = pengirim.saldo,                                                    
                            transfer_masuk = 0,
                            setor_tunai = 0,
                            transfer = data['transfer'],
                            debit = 0,
                            kredit = 0,
                            tarik_tunai = 0,
                            saldo_masuk = 0,
                            saldo_keluar = data['transfer']
                        )
                        t_ = Transfer(
                            waktu = datetime.now(),                                                     
                            transfer = data['transfer'],                                                   
                            id_account_pengirim = data['id_account'],               
                            id_cabang_pengirim = data['id_cabang'],
                            id_account_penerima = data['id_account'],                
                            id_cabang_penerima = data['id_cabang']
                        )
                        penerima.saldo = penerima.saldo + data['transfer']
                        transaksi_pengirim.saldo_masuk = 0
                        transaksi_pengirim.saldo_keluar = data['transfer']
                        transaksi_penerima.saldo_masuk += data['transfer']
                        transaksi_penerima.saldo_keluar = 0
                        db.session.add(t)
                        db.session.add(t_)
                        db.session.commit()
                        return { 
                            "waktu" : datetime.now(),
                            "saldo_sebelum" : saldo_sebelum,
                            "saldo_setelah" : pengirim.saldo,                                                    
                            "transfer" : data['transfer']
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





# ----------------------------------------------------------------------------------------------->>> TRANSAKSI (belom)
# @app.route('/transaksi/debit', methods=['POST']) #by user #mirip seperti transfer
# def post_transaksi_debit():
#     decode = request.headers.get('Authorization')
#     id_nasabah = auth_nasabah(decode)
#     if id_nasabah :
#         data = request.get_json()
#         accounts = Account.query.filter_by(id_account=data['id_account']).first()
#         day_off = datetime.now() - accounts.last_update
#         no_activity = day_off.days    
#         if no_activity > 90 :
#             accounts.status == "Tidak Aktif"
#             return {
#                     "pesan" : "akun anda tidak aktif"
#                 }, 400
#         else :
#             accounts.status == "Aktif"
#             if accounts.saldo - data['debit'] > 50000 :
#                 accounts.saldo = accounts.saldo - data['debit']
#                 accounts.last_update == datetime.now()
#                 saldo_sebelum = accounts.saldo + data['debit']
#                 t = Transaksi( 
#                     waktu = datetime.now(),                                                    
#                     saldo_masuk = 0,
#                     transfer = 0,
#                     debit = data['debit'],
#                     kredit = 0,
#                     tarik_tunai = 0,
#                     id_account = data['id_account']
#                     )
#                 db.session.add(t)
#                 db.session.commit()
#                 return { 
#                     "waktu" : datetime.now(),
#                     "saldo_sebelum" : saldo_sebelum,
#                     "saldo_setelah" : accounts.saldo,                                                    
#                     "debit" : data['debit']
#                 }, 201
#             else:
#                 return {
#                     "pesan": "saldo anda tidak cukup"
#                 }, 400
#     else :
#         return {
#             'pesan': 'Akses Ditolak !!'
#         }, 400

# @app.route('/transaksi/kredit', methods=['POST']) #by user
# def post_transaksi_kredit():
#     decode = request.headers.get('Authorization')
#     id_nasabah = auth_nasabah(decode)
#     if id_nasabah :
#         data = request.get_json()
#         accounts = Account.query.filter_by(id_account=data['id_account']).first()
#         day_off = datetime.now() - accounts.last_update
#         no_activity = day_off.days    
#         if no_activity > 90 :
#             accounts.status == "Tidak Aktif"
#             return {
#                     "pesan" : "akun anda tidak aktif"
#                 }, 400
#         else :
#             accounts.status == "Aktif"
#             if accounts.saldo - data['kredit'] > 50000 :
#                 accounts.saldo = accounts.saldo - data['kredit']
#                 accounts.last_update == datetime.now()
#                 saldo_sebelum = accounts.saldo + data['kredit']
#                 t = Transaksi( 
#                     waktu = datetime.now(),                                                    
#                     saldo_masuk = 0,
#                     transfer = 0,
#                     debit = 0,
#                     kredit = data['kredit'],
#                     tarik_tunai = 0,
#                     id_account = data['id_account']
#                     )
#                 db.session.add(t)
#                 db.session.commit()
#                 return { 
#                     "waktu" : datetime.now(),
#                     "saldo_sebelum" : saldo_sebelum,
#                     "saldo_setelah" : accounts.saldo,                                                    
#                     "kredit" : data['kredit']
#                 }, 201
#             else:
#                 return {
#                     "pesan": "saldo anda tidak cukup"
#                 }, 400
#     else :
#         return {
#             'pesan': 'Akses Ditolak !!'
#         }, 400

# @app.route('/transaksi/tarik_tunai', methods=['POST']) #by user
# def post_transaksi_tarik_tunai():
#     decode = request.headers.get('Authorization')
#     id_nasabah = auth_nasabah(decode)
#     if id_nasabah:
#         data = request.get_json()
#         accounts = Account.query.filter_by(id_account=data['id_account']).first()
#         day_off = datetime.now() - accounts.last_update
#         no_activity = day_off.days    
#         if no_activity > 90 :
#             accounts.status == "Tidak Aktif"
#             return {
#                     "pesan" : "akun tidak aktif"
#                 }, 400
#         else :
#             accounts.status == "Aktif"
#             if accounts.saldo - data['tarik_tunai'] > 50000 :
#                 accounts.saldo = accounts.saldo - data['tarik_tunai']
#                 accounts.last_update == datetime.now()
#                 saldo_sebelum = accounts.saldo + data['tarik_tunai']
#                 t = Transaksi( 
#                     waktu = datetime.now(),                                                    
#                     saldo_masuk = 0,
#                     transfer = 0,
#                     debit = 0,
#                     kredit = 0,
#                     tarik_tunai = data['tarik_tunai'],
#                     id_account = data['id_account']
#                     )
#                 db.session.add(t)
#                 db.session.commit()
#                 return { 
#                     "waktu" : datetime.now(),
#                     "saldo_sebelum" : saldo_sebelum,
#                     "saldo_setelah" : accounts.saldo,                                                    
#                     "tarik_tunai" : data['tarik_tunai']
#                 }, 201
#             else:
#                 return {
#                     "pesan": "saldo anda tidak cukup"
#                 }, 400
#     else :
#         return {
#             'pesan': 'Akses Ditolak !!'
#         }, 400

@app.route('/transaksi/history', methods=['GET']) #by user
def get_transaksi():
    decode = request.headers.get('Authorization')
    id_nasabah = auth_nasabah(decode)
    if id_nasabah:                                          
        transaksi = Transaksi.query.filter_by(id_transaksi=id_nasabah).all()
        arr = []
        for i in transaksi :
            arr.append(i.id_transaksi)
            return jsonify([
                {
                    'id_account' : transaksi.id_account,
                    'waktu' : transaksi.waktu,                                                    
                    'saldo_masuk' : transaksi.saldo_masuk,
                    'transfer' : transaksi.transfer,
                    'debit' : transaksi.debit,
                    'kredit' : transaksi.kredit,
                    'tarik_tunai' : transaksi.tarik_tunai
                } for transaksi in Transaksi.query.all() 
            ]), 201

    




