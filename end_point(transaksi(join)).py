#### VERSI DIJADIKAN SATU END POINT
# @app.route('/account/transaksi', methods=['POST']) #by user
# def post_transaksi():
#     decode = request.headers.get('Authorization')
#     nasabah_id = auth_nasabah(decode)
#     accounts = Account.query.filter_by(id_nasabah=nasabah_id).all()
#     data = request.get_json() 
#     arr = []
#     for i in accounts :
#         arr.append(i.no_rekening) 
#         day_off = datetime.now() - accounts.last_update
#         data  = request.get_json()
#         if day_off > datetime.timedelta(days=90) :
#             accounts.status == "Tidak Aktif"
#             return {
#                     "pesan" : "akun anda tidak aktif"
#                 }, 400
#         if day_off < datetime.timedelta(days=90) :
#             accounts.status == "Aktif"
#             t = Transaksi( 
#                 waktu = datetime.now(),
#                 no_rekening = accounts.no_rekening,
#                 status = accounts.status,
#                 saldo = accounts.saldo,                                                    
#                 saldo_masuk = data['saldo_masuk'],
#                 transfer = data['transfer'],
#                 debit = data['debit'],
#                 kredit = data['kredit'],
#                 tarik_tunai = data['tarik_tunai'],
#                 id_account = data['id_account'] 
#             )
#             if data['type_transaksi'] == "transfer" or data['type_transaksi'] == "debit" or data['type_transaksi'] == "kredit" or data['type_transaksi'] == "tarik_tunai" :
#                 if accounts.saldo - data['type_transaksi'] > 50000 :
#                     accounts.saldo -= data['type_transaksi']
#                     accounts.last_update == datetime.now()
#                     db.session.commit(t)
#                     return { 
#                         "waktu" : data['waktu'],
#                         "no_rekening" : accounts.no_rekening,
#                         "status" : accounts.status,
#                         "saldo" : accounts.saldo,                                                    
#                         "transfer" : data['transfer'],
#                         "debit" : data['debit'],
#                         "kredit" : data['kredit'],
#                         "tarik_tunai" : data['tarik_tunai']
#                 }, 201
#                 else:
#                     return {
#                         "pesan": "saldo tidak cukup"
#                     }, 400

#             elif data["type_transaksi"] == "saldo_masuk" :
#                     accounts.saldo += data['type_transaksi']
#                     accounts.last_update == datetime.now()
#                     db.session.commit()
#                     return {
#                         "saldo_masuk" : data['saldo_masuk']
#                     }, 201