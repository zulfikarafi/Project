import base64
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SECRET_KEY']='secret'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:sql123@localhost:5432/dbportaljob?sslmode=disable'
db = SQLAlchemy(app)


class Jobseeker(db.Model):
    idjobseeker = db.Column(db.Integer, primary_key=True, index=True, nullable=False, unique=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    bio = db.Column(db.String(500), nullable=False)
    jobseeker_rel = db.relationship('Application', cascade="all,delete", backref='jobseeker')

class Employer(db.Model):
    idemployer = db.Column(db.Integer, primary_key=True, index=True, nullable=False, unique=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    companyname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    bio = db.Column(db.String(500), nullable=False)
    job_rel = db.relationship('Job', backref="employer")

class Job(db.Model):  
    idjob = db.Column(db.Integer, primary_key=True, index=True, nullable=False, unique=True)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    requirement = db.Column(db.String(500), nullable=False)
    salary = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    area = db.Column(db.String(50), nullable=False)
    postingdate = db.Column(db.Date, nullable=False)
    expiredate = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    idemployer = db.Column(db.Integer, db.ForeignKey('employer.idemployer'), nullable=False)
    job_rel = db.relationship('Application', backref='job')

class Application(db.Model):
    idapplication = db.Column(db.Integer, primary_key=True, index=True, nullable=False, unique=True)
    status = db.Column(db.String(50), nullable=False) 
    job_title = db.String(50)
    employer_companyname = db.String(50)
    job_description = db.Column(db.String(500), nullable=False)
    job_postingdate = db.Column(db.Date, nullable=False)
    job_expiredate = db.Column(db.Date, nullable=False)
    idjobseeker = db.Column(db.Integer, db.ForeignKey('jobseeker.idjobseeker'), nullable=False)
    idjob = db.Column(db.Integer, db.ForeignKey('job.idjob'), nullable=False)



# ------------------------------------------------------------------------------------->>> generate first if db is empty
# db.create_all()
# db.session.commit()



def auth_jobseeker(auth):
    encode = base64.b64decode(auth[6:])
    str_encode = encode.decode('ascii')
    lst = str_encode.split(':')
    username = lst[0]
    password = lst[1]   
    jobseeker = Jobseeker.query.filter_by(username=username).filter_by(password=password).first()
    if jobseeker:
        return str(jobseeker.idjobseeker)
    else:
        return 
        
def auth_employer(auth):
    encode = base64.b64decode(auth[6:])
    str_encode = encode.decode('ascii')
    lst = str_encode.split(':')
    username = lst[0]
    password = lst[1]   
    employer = Employer.query.filter_by(username=username).filter_by(password=password).first()
    if employer:
        return (employer.idemployer)
    else:
        return 0



# ------------------------------------------------------------------------------------->>> Home
@app.route('/', methods=['GET'])
def home():
    return jsonify(
        "Home"
    )



# ------------------------------------------------------------------------------------->>> Jobseeker
@app.route('/jobseeker/register', methods=['POST'])
def create_jobseeker():
    data = request.get_json(force=True)
    jobseeker = Jobseeker(
        username = data['username'],
        password = data['password'],
        name = data['name'],
        email = data['email'],
        bio = data['bio']
	)
    try:
        db.session.add(jobseeker)
        db.session.commit()
    except:
        return {
            "Message": "Account data save failed"
        }, 400
    return {
        "Message": "Account data save success"
    }, 201

@app.route('/jobseeker/profile', methods=['GET'])
def get_jobseeker_login():
    decode = request.headers.get('Authorization')
    allow = auth_jobseeker(decode)
    jobseeker = Jobseeker.query.filter_by(idjobseeker=allow).first()
    if not jobseeker :
        return {
            'message': 'ACCESS DENIED !!'
        }, 400
    else :
        return jsonify([
            {
                'name':jobseeker.name,
                'username':jobseeker.username,
                'password':jobseeker.password,
                'email':jobseeker.email,
                'bio':jobseeker.bio
            }
            ]), 201
        
@app.route('/jobseeker/updateprofile', methods=['PUT'])
def update_jobseeker():
    decode = request.headers.get('Authorization')
    allow = auth_jobseeker(decode)
    data  = request.get_json()
    jobseeker = Jobseeker.query.filter_by(idjobseeker=allow).first()
    if not jobseeker :
        return {
            "Message": 'ACCESS DENIED !'
        }
    else :
        jobseeker.username = data['username']
        jobseeker.password = data['password']
        jobseeker.name = data['name']
        jobseeker.email = data['email']
        jobseeker.bio = data['bio']
        db.session.commit()
        return {
            "Message": "Account data update success"
            }, 201

@app.route('/jobseeker/deleteaccount', methods=['DELETE'])
def delete_jobseeker():
    decode = request.headers.get('Authorization')
    allow = auth_jobseeker(decode)
    jobseeker = Jobseeker.query.filter_by(idjobseeker=allow).first()
    if not allow :
        return {
            "Message": 'ACCESS DENIED !'
        }
    else :
        db.session.delete(jobseeker)
        db.session.commit()
        return {
            "Message": " Account delete success"
            }, 201



# ------------------------------------------------------------------------------------->>> Employer
@app.route('/searchjobseeker', methods=['POST']) #SALAHH
def search_jobseeker():
    decode = request.headers.get('Authorization')
    allow = auth_employer(decode)
    jobseeker = Jobseeker.query.filter_by(idjobseeker=allow).first()
    if not jobseeker :
        return {
            'message' : 'ACCESS DENIED !!'
        }, 400
    else :
        return jsonify([
            {
                'name':jobseeker.name,
                'username':jobseeker.username,
                'password':jobseeker.password,
                'email':jobseeker.email,
                'bio':jobseeker.bio
            }
        ]), 201       

@app.route('/employer/register', methods=['POST'])
def create_employer():
    data = request.get_json(force=True)
    employer = Employer(
        username = data['username'],
        password = data['password'],
        companyname = data['companyname'],
        email = data['email'],
        bio = data['bio']
	)
    try:
        db.session.add(employer)
        db.session.commit()
    except:
        return {
            "Message": "Account data save failed"
        }, 400
    return {
        "Message": "Account data save success"
    }, 201

@app.route('/employer/profile', methods=['GET'])
def get_employer_login():
    decode = request.headers.get('Authorization')
    allow = auth_employer(decode)
    employer = Employer.query.filter_by(idemployer=allow).first()
    if not employer :
        return {
            'message': 'ACCESS DENIED !!'
        }, 400
    else:
        return jsonify([
            {
                'name':employer.companyname,
                'username':employer.username,
                'password':employer.password,
                'email':employer.email,
                'bio':employer.bio
            }
        ]), 201

@app.route('/employer/updateprofile', methods=['PUT'])
def update_employer():
    decode = request.headers.get('Authorization')
    allow = auth_employer(decode)
    data  = request.get_json()
    employer = Employer.query.filter_by(idemployer=allow).first()
    if not employer :
        return {
            "Message": 'ACCESS DENIED !'
        }
    else :
        employer.username = data['username']
        employer.password = data['password']
        employer.companyname = data['companyname']
        employer.email = data['email']
        employer.bio = data['bio']
        db.session.commit()
        return {
            "Message": "Account data update success"
            }, 201

@app.route('/employer/deleteaccount', methods=['DELETE'])
def delete_employer():
    decode = request.headers.get('Authorization')
    allow = auth_jobseeker(decode)
    employer = Employer.query.filter_by(idjobseeker=allow).first()
    if not employer :
        return {
            "Message": 'ACCESS DENIED !'
        }
    else :
        db.session.delete(employer)
        db.session.commit()
        return {
            "Message": "Account delete success"
        }, 500    



# ------------------------------------------------------------------------------------>>> Job
@app.route('/getajob/<id>', methods=['GET'])
def get_ajob(id):
    decode = request.headers.get('Authorization')
    allow = auth_employer(decode)
    job = Job.query.filter_by(idjob=id).filter_by(idemployer = allow).first()
    if not job :
        return {
            "Message": 'ACCESS DENIED !'
        }
    else:
        return jsonify([
            {
                "Job_Title" : job.title,
	            "Job_Description" : job.description,
	            "Job_Requirement" : job.requirement,
                "Job_Salary" : job.salary,
	            "Job_Category" : job.category,
	            "Area" : job.area,
	            "Posting_Date" : job.postingdate,
	            "Expired_Date" :	job.expiredate,
	            "Status" : job.status
            }
        ]), 201

@app.route('/getavailablejob', methods=['GET'])
def get_availablejob():
    job = Job.query.filter_by(status='Available').all()
    if job :
        return jsonify([
        {
            "Job_Title" : x.title,
            "Job_Description" : x.description,
            "Job_Requirement" : x.requirement,
            "Job_Salary" : x.salary,
            "Job_Category" : x.category,
            "Area" : x.area,
            "Posting_Date" : x.postingdate,
            "Expired_Date" : x.expiredate,
            "Status" : x.status
        } for x in job
        ]), 201
    else :
        return {
            "Message": 'No available job'
        }
        
@app.route('/getjoboncriteria', methods=['GET'])  # BELUM BERES
def get_joboncriteria():
    data = request.get_json()
    if data['title'] == "" and data['category'] == "" and data['salary'] == "" and data['area'] == "" :
        return jsonify([
        {
            "Job_Title" : job.title,
            "Job_Description" : job.description,
            "Job_Requirement" : job.requirement,
            "Job_Salary" : job.salary,
            "Job_Category" : job.category,
            "Area" : job.area,
            "Posting_Date" : job.postingdate,
            "Expired_Date" : job.expiredate,
            "Status" : job.status
        } for job in Job.query.all()
        ]), 200
    elif data['title'] != "" or data['area'] != "" :
        result = db.engine.execute("select * from job where category ilike '%IT%' or title ilike '%Project Manager%' or area ilike '%Bandung%' order by postingdate desc")
        arr =[]
        for x in result:
            arr.append([
            {
                "Job_Title" : x.title,
                "Job_Description" : x.description,
                "Job_Requirement" : x.requirement,
                "Job_Salary" : x.salary,
                "Job_Category" : x.category,
                "Area" : x.area,
                "Posting_Date" : x.postingdate,
                "Expired_Date" : x.expiredate,
                "Status" : x.status
            }
            ])
        return jsonify(arr), 200

@app.route('/create/job', methods=['POST'])
def create_job():
    decode = request.headers.get('Authorization')
    allow = auth_employer(decode)
    data = request.get_json()
    employer = Employer.query.filter_by(idemployer=allow).first()
    if not employer : 
        return {
            "Message": 'ACCESS DENIED !'
        }
    else :
        job = Job(
            title = data['title'],
            description = data['description'],
            requirement = data['requirement'],
            salary = data['salary'],
            category = data['category'],
            area = data['area'],
            postingdate = data['postingdate'],
            expiredate = data['expiredate'],
            status = data['status'],
            idemployer = employer.idemployer
	    )
        db.session.add(job)
        db.session.commit()
        return {
            "Message": "Account data save success"
        }, 201

@app.route('/update/job/<id>', methods=['PUT'])
def update_job(id): 
    decode = request.headers.get('Authorization')
    allow = auth_employer(decode)
    data = request.get_json()
    job = Job.query.filter_by(idjob=id).filter_by(idemployer = allow).first()
    if not job :
        return {
                "Message": "ID job input isn't correct"
            }, 400
    else :
        job.title = data['title']
        job.description = data['description']
        job.requirement = data['requirement']
        job.salary = data['salary']
        job.category = data['category']
        job.area = data['area']
        job.postingdate = data['postingdate']
        job.expiredate = data['expiredate']
        job.status = data['status']
        db.session.commit()
        return {
            "Message": "Account data update success"
            }, 201

@app.route('/delete/job/<id>', methods=['DELETE'])
def delete_job(id):
    decode = request.headers.get('Authorization')
    allow = auth_employer(decode)
    job = Job.query.filter_by(idjob=id).filter_by(idemployer=allow).first()
    if not job :
        return {
            "Message": 'ACCESS DENIED !'
            }
    else : 
        db.session.delete(job)
        db.session.commit()
        return {
            "Message": " Account delete success"
        }, 201



# ------------------------------------------------------------------------------------>>> Application
@app.route('/application', methods=['GET'])
def get_application():
    result = db.engine.execute(f'''select "application".status, job.title, employer.companyname, job.description, job.postingdate, job.expiredate from "application" join job on "application".idjob = job.idjob join employer on "application".idemployer=employer.idemployer''')
    for x in result:
        return jsonify([
            {
                'Application Status' : x.status,
                'Job Title': x.title,
                'Company name': x.companyname,
                'Job Description': x.description,
                'Job Posting Date' : x.postingdate,
                'Job Expired Date' : x.expiredate
            }
        ])  

@app.route('/application/id', methods=['POST'])
def create_application(id):
    decode = request.headers.get('Authorization')
    allow = auth_jobseeker(decode)
    if allow == id:
        data = request.get_json(force=True)
        job = Job.query.filter_by(idjob=data['idjob']).first()
        employer = Employer.query.filter_by(idemployer=data['idemployer']).first()
        application = Application(
            status = data['status'],
            job_description = job.description,
            employer_companyname = employer.companyname,
            job_postingdate = job.postingdate,
            job_expiredate = job.expiredate,
            idjobseeker = data['idjobseeker'],
            idemployer = data['idemployer'],
            idjob = data['idjob']
        )
    try:
        db.session.add(application)
        db.session.commit()
    except:
        return {
            "Message": "Application save failed"
        }, 400
    return {
        "Message": "Application save success"
    }, 201

@app.route('/application/<id>', methods=['PUT'])
def update_application(id):
    data  = request.get_json()
    application = Application.query.filter_by(idapplication=id).first()
    application.status = data['status']
    try:
        db.session.commit()
    except:
        return {
            "Message": "save data failed"
        }, 400
    return {
        "Message": "save data success"
    }, 201



if __name__ == "__main__":
    app.run()