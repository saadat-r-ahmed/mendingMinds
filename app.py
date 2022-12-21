# ALL IMPORTS #
from flask import Flask, render_template, url_for, request, redirect, session, json, flash
from model import modelObj
import model

app = Flask(__name__)
app.secret_key = "this-is-the-maxwell"
app.register_blueprint(modelObj, url_prefix='')

##############################################
####       USER LOGIN AND LOGOUT          ####
##############################################
# TODO: ✅ user login module created
@app.route('/login/user', methods = ['post', 'get'])
def ctrlLoginUser():
    '''RENDERS LOGIN PAGE IF SESSION NOT INITIALIZED
    OTHERWISE GENERATES USERDASHBAORD'''
    if 'userName' in session:
        return render_template('userDashboard.html', userName = session['userName'])
    else:
        return render_template('userLogin.html')

# TODO: ✅ professional login module created
@app.route('/login/prof', methods = ['post', 'get'])
def ctrlLoginProf():
    '''RENDERS LOGIN PAGE IF SESSION NOT INITIALIZED
    OTHERWISE GENERATES PROFDASHBAORD'''
    if 'profName' in session:
        return render_template('profDashboard.html', userName = session['profName'])
    else:
        return render_template('profLogin.html')

# TODO: ✅ all user authintication module created
@app.route('/login/user/authinticate', methods=['POST', 'GET'])
def ctrlUserAuthinticate():
    print('🔰RECEIVING USER LOGIN REQUEST🔰')
    if request.method == "POST":
        userEmail = request.form["userEmail"]
        userPass = request.form["userPass"]
        manType = request.form["manType"]

        validate = model.userAuthinticate(manType= manType, 
                                          userEmail = userEmail, 
                                          userPass = userPass)
        if validate == False:
            return render_template('error.html', 
            head = 'UNABLE TO LOGIN', 
            msg = 'The provided email or the password did not match with the database. Please try again later.')
        else:
            if manType == 'user':
                session['userEmail'], session['userName'] = validate
                print(session['userEmail'], session['userName'])
                return redirect('/login/user')
            elif manType == 'prof':
                session['profEmail'], session['profName'] = validate
                print(session['profEmail'], session['profName'])
                return redirect('/login/prof')


# TODO: ✅ DONE
@app.route('/user/writePost', methods = ['GET', 'POST'])
def writePost():
    if 'userName' in session:
        return render_template('writePost.html', userName = session['userName'])

# TODO: ✅ Logout 
@app.route('/logout/user')
@app.route('/user/logout')
def userLogout():
    session.pop('userEmail', None)
    session.pop('userName', None)
    flash('Logging out complete')
    return redirect('/login/user')


@app.route('/logout/prof')
@app.route('/prof/logout')
def profLogout():
    session.pop('profEmail', None)
    session.pop('profName', None)
    flash('Logging out complete')
    return redirect('/login/prof')
##############################################


##########################################################
####       MAKING POST, VIEWING POST AND MAKING COMMENT
##########################################################
# TODO: ✅ DONE
@app.route('/user/postRequest', methods = ['POST', 'GET'])
def postRequest():
    '''TAKES IN POST DATA AND COMMITS IT TO DB'''
    if 'userName' in session:
        postText = request.form["postText"]
        val = model.makepost(session['userEmail'], postText)
        if val == True:
            return render_template('error.html', 
            head = 'Success Message', msg = 'Your post was uploaded')
        else:
            return render_template('error.html', 
            head = 'Failed Message', msg = 'Something went wrong, Please try again later.')


# TODO: ✅ DONE
@app.route('/login/prof/showAllPosts', methods = ['POST', 'GET'])
def showAllUserPost():
    '''shows all the posts of the users'''
    if 'profName' in session:
        allPosts = model.fetchComments()
        return render_template('profShowAllUserPost.html', allPosts = allPosts,
                                userName = session['profName'])
    else:
        return redirect('/login/prof')


# TODO: ✅ DONE
@app.route('/login/prof/makePosts', methods = ['POST', 'GET'])
def profMakePost():
    if 'profName' in session:
        profComment = request.form['profComment']
        postID = request.form['postID']
        model.makeComment(postID, profComment)
        return redirect('/login/prof/showAllPosts')



# TODO: ✅ DONE
@app.route('/login/user/showAllPosts', methods = ['POST', 'GET'])
def showUserAllPosts():
    '''shows all the posts of the users'''
    if 'userName' in session:
        allPosts = model.fetchComments()
        return render_template('userShowAllUserPost.html', allPosts = allPosts,
                                userName = session['userName'])
    else:
        return redirect('/login/user')



@app.route('/login/user/requestAppointment', methods = ['POST', 'GET'])
def userRequestAppointment():
    if 'userName' in session:
        docs = model.getDocs()
        return render_template('takeAppointment.html', userName = session['userName'], docs = docs)

@app.route('/login/user/requestAppointment/req', methods = ['POST', 'GET'])
def reqAppointment():
    if 'userName' in session:
        profEmail = request.form['docID']
        model.updateAssignmnet(userEmail = session['userEmail'], profEmail =  profEmail)
        return render_template('error.html', head = 'Appointment Placed', 
        msg = 'The doctor will let you know about the time and url, plesae check your appintment list')

@app.route('/login/prof/showAppointmentReq', methods = ['POST', 'GET'])
def showAppointmentsReq():
    if 'profName' in session:
        getQueue = model.getQueue(session['profEmail'])

        return render_template('acceptOrDenyReq.html', queue = getQueue, userName = session['profName'])
    else:
        return render_template('profLogin.html')


@app.route('/login/prof/user/appointment/makeChange', methods = ['POST', "GET"])
def profAppointmentChange():
    if 'profEmail' in session:
        reqID = request.form['reqID']
        status = request.form['status']
        date = request.form['appointmentDate']
        model.profAcceptOrDenyAppointment(reqID, status, date)
        return redirect('/login/prof/showAppointmentReq')
    else:
        return redirect('/login/prof')


@app.route('/login/user/showAllAppointments', methods = ['POST', "GET"])
def userShowAllAppointments():
    if 'userName' in session:
        data = model.userAppointments(session['userEmail'])
        return render_template('userShowAllAppointments.html', tableData = data, userName = session['userName'])
    else:
        return redirect('/login/user')

@app.route('/login/user/NOT FIXED YET')
def noDateFixed():
    return render_template('error.html', head = 'Invalid Link', 
    msg = 'Dear user, your zoom meeting has not been created yet. It will be created when the doctor accepts the request for appointment.')


@app.route('/login/prof/showAllAppointments')
def profShowAllAppointments():
    if 'profEmail' in session:
        data = model.docAppointments(session['profEmail'])
        return render_template('profShowAllAppointments.html', userName = session['profName'], tableData = data)

@app.route('/')
def homePage():
    return render_template('homepage.html')

if __name__ == '__main__':
    app.run(debug=True, port = 8080)
