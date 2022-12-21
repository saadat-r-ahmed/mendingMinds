from flask import Blueprint, redirect, session, url_for
import numpy as np
import zoomMeeting as zoom
modelObj = Blueprint("model", __name__, static_folder = "static", template_folder = "templates")

###############################
#### SQL MODULES
###############################
import mysql.connector as con


def fetchSQL(qry: str) -> list:
    '''Input: SQL query and 
    returns: a list of Rows'''
    access = con.connect(
        host = 'sql6.freesqldatabase.com',
        user = 'sql6584665',
        database = 'sql6584665',
        password = 'Bk4Mw1ALIC'
        )
    cur = access.cursor()
    cur.execute(qry)
    r = cur.fetchall()
    return r    

def commitSQL(qry: str) -> None:
    access = con.connect(
        host = 'sql6.freesqldatabase.com',
        user = 'sql6584665',
        database = 'sql6584665',
        password = 'Bk4Mw1ALIC'
        )
    cur = access.cursor()
    cur.execute(qry)
    access.commit()

###############################
#### SQL MODULES
###############################

def userAuthinticate(manType, userEmail, userPass) -> bool:
    '''returns TRUE: if user validated, else FALSE'''
    if manType == 'user':
        table = 'userData'
    elif manType == 'prof':
        table = 'profData'
    values = fetchSQL(f'select * from {table} where email = "{userEmail}"')
    if len(values) == 1 and values[0][2] == userPass:
        return (values[0][0:2])
    else:
        return False


def makepost(userEmail, postText) -> bool:
    qry = f'''
    INSERT INTO `userPost` (`postID`, `email`, `postText`) VALUES (NULL, '{userEmail}', '{postText}')
    '''
    try:
        commitSQL(qry)
        return True
    except:
        return False


def fetchComments() -> list:
    postID = sorted(list(np.array(fetchSQL('''select postID from userPost'''))[:,0]), reverse = True)
    comments = []
    postDetails = []
    for i in range(len(postID)):
        c = fetchSQL(f'SELECT profName, comment FROM profComment WHERE postID = "{postID[i]}" ORDER BY commentID DESC')
        email = fetchSQL(f'select email from userPost where postID = {postID[i]}')[0][0]
        name = fetchSQL(f'select name from userData where email = "{email}"')[0][0]
        postText = fetchSQL(f'select postText from userPost where postID = "{postID[i]}"')[0][0]
        comments.append([[postID[i], name, email, postText], c])
    return comments


def makeComment(postID, profComment):
    qry = f'''
    INSERT INTO `profComment` (`commentID`, `postID`, `profName`, `comment`) VALUES (NULL, '{postID}', '{session['profName']}', '{profComment}')
    '''
    print(qry)
    try:
        commitSQL(qry)
        return True
    except:
        return False


def getDocs():
    docs = fetchSQL(f'SELECT name, email FROM profData')
    return docs


def updateAssignmnet(userEmail, profEmail):
    commitSQL(f'''INSERT INTO `requestTable` (`reqID`, `userEmaill`, `profEmail`, `status`) 
    VALUES (NULL, '{userEmail}', '{profEmail}', 'In Queue')''')
    return True


def getQueue(profEmail):
    req = fetchSQL(f'''SELECT * FROM `requestTable` where profEmail = '{profEmail}' and status = 'In Queue' ORDER BY reqID DESC;''')
    return req


def profAcceptOrDenyAppointment(reqID, status, date):
    if status == 'accept':
        zoomURL = zoom.createMeeting()
        qry = f'''
        UPDATE requestTable 
        SET status = 'accept', meetingURL = '{zoomURL}', appointmentDate = '{date}'
        WHERE reqID = {reqID}
        '''
        commitSQL(qry)
    else:
        qry = f'''
        UPDATE requestTable 
        SET status = 'deny'
        WHERE reqID = {reqID}
        '''
        commitSQL(qry)


def userAppointments(userEmail):
    data = fetchSQL(f'''
    SELECT * FROM `requestTable` 
    WHERE 
        `userEmaill` = '{userEmail}' 

    ORDER BY 
    FIELD(`status`, "accept", "In Queue", "deny"),
    `appointmentDate` ASC
    ''')
    return data


def docAppointments(docEmail):
    data = fetchSQL(f'''
    SELECT * FROM `requestTable` 
    WHERE 
        `profEmail` = '{docEmail}'
        AND
        `status` = 'accept'
        AND
    `appointmentDate` >= CURRENT_DATE
    ORDER BY 
    FIELD(`status`, "accept", "In Queue", "deny"),
    `appointmentDate` ASC
    ''')
    return data
