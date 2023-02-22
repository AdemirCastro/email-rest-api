import pathlib
from fastapi import APIRouter
from dependencies.emails.emails import email
from models.emails import *

router = APIRouter(
    prefix='/email',
    tags=['email'],
    )

@router.post('/emails',
             response_model= Send_post_response_model, 
             description="Send a email."
    )
async def send(request: EmailSend):
    request_json = request.dict()

    mail = email(
        login       =request_json['login'],
        password    =request_json['password'],
        smtp_server =request_json['smtp_server'],
        imap_server =request_json['imap_server']
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
             response_model= Mailboxes_get_response_model, 
             description="Get mailboxes."
    )
def get_boxes(Request: EmailCredentials):
    request_json = Request.dict()
    mail = email(
        login       =request_json['login'],
        password    =request_json['password'],
        smtp_server =request_json['smtp_server'],
        imap_server =request_json['imap_server']
        )
    response = {"mailboxes": mail.get_mailboxes()}
    return response


@router.get('/emails_uids',
            response_model=UIDs_get_response_model,
            description='Get email UIDs, attending given criterias.')
def get_uids(Request: GetEmailsUIDsForm):
    request_json = Request.dict()
    mail = email(
        login      = request_json['login'],
        password   = request_json['password'],
        smtp_server= request_json['smtp_server'],
        imap_server= request_json['imap_server']
    )
    response = {
        'uids': mail.get_emails_uids(
                    mailbox= request_json['mailbox'],
                    criterias_dict= request_json['criterias']
                    )
        }
    return response


@router.get('/emails',
            response_model=Emails_get_response_model,
            description='Get email messages, given mailbox and Uids.')
def get_mails(Request: EmailUID):
    request_json = Request.dict()
    mail = email(
        login      = request_json['login'],
        password   = request_json['password'],
        smtp_server= request_json['smtp_server'],
        imap_server= request_json['imap_server']
        )
    response = {
        'emails': mail.get_emails(
            request_json['uid'],
            request_json['mailbox']
        )
    }
    return response


@router.put('/emails/move',
            response_model=Move_put_desponse_model,
            description='Move email message from one mailbox to another.')
def move_email(Request: PutEmailsMove):
    request_json = Request.dict()
    mail = email(
        login      = request_json['login'],
        password   = request_json['password'],
        smtp_server= request_json['smtp_server'],
        imap_server= request_json['imap_server']
        )
    response = mail.move_email(
        from_box=request_json['from_box'],
        uid=request_json['uid'],
        to_box=request_json['to_box']
    )
    return response