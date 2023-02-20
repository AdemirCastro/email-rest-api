import pathlib
from fastapi import APIRouter
from dependencies.emails.emails import email
from models.emails import *

router = APIRouter(
    prefix='/email',
    tags=['email'],
    )

@router.post('/send',
             response_model= send_post_response_model, 
             description="Send a email."
    )
async def send(request: EmailSend):
    request_json = request.dict()

    mail = email(
        login       =request_json['login'],
        password    =request_json['password'],
        smtp_server =request_json['smtp_server']
        )
    response = {"errors": mail.send_email(
                            sender      =request_json['sender'],
                            recipients  =request_json['recipients'],
                            Cc          =request_json['Cc'],
                            subject     =request_json['subject'],
                            body        =request_json['body'],
                            body_type   =request_json['body_type'],
                            attachments =request_json['attachments']
                            )
                        }
    return response

@router.get('/mailboxes',
             response_model= mailboxes_get_response_model, 
             description="Get mailboxes."
    )
def get_boxes(Request: EmailCredentials):
    request_json = Request.dict()
    mail = email(
        login       =request_json['login'],
        password    =request_json['password'],
        imap_server =request_json['imap_server']
        )
    response = {"mailboxes": mail.get_mailboxes()}
    return response

@router.get('/get_emails',
            response_model=getEmails_get_response_model,
            description='Get email messages, given mailbox and Uids.')
def get_mails(Request: EmailUIDs):
    request_json = Request.dict()
    mail = email(
        login      = request_json['login'],
        password   = request_json['password'],
        smtp_server= request_json['smtp_server'],
        imap_server= request_json['imap_server']
        )
    response = {
        'emails': mail.get_emails(
            request_json['uids'],
            request_json['mailbox']
        )
    }
    return response