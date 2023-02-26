import pathlib
from fastapi import APIRouter
from dependencies.emails.emails import email
from models.emails import *

router = APIRouter(
    prefix='/email',
    )

@router.post('/messages',
             response_model= Send_post_response_model, 
             description="Send a email."
    )
async def send_message(request: EmailSend):
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
def get_mailboxes(Request: EmailCredentials):
    request_json = Request.dict()
    mail = email(
        login       =request_json['login'],
        password    =request_json['password'],
        smtp_server =request_json['smtp_server'],
        imap_server =request_json['imap_server']
        )
    response = {"mailboxes": mail.get_mailboxes()}
    return response


@router.get('/messages/uids',
            response_model=UIDs_get_response_model,
            description='Get UIDs of email messages attending given criteria.')
def get_messages_UIDs(Request: GetEmailsUIDsForm):
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


@router.get('/messages',
            response_model=EmailMessage,
            description='Get email message, given mailbox path and message UID.')
def get_message(Request: EmailUID):
    request_json = Request.dict()
    mail = email(
        login      = request_json['login'],
        password   = request_json['password'],
        smtp_server= request_json['smtp_server'],
        imap_server= request_json['imap_server']
        )
    response = mail.get_email(request_json['uid'], request_json['mailbox'])

    return response


@router.put('/messages/move',
            response_model=Move_put_desponse_model,
            description='Move email message from one mailbox to another.')
def move_message(Request: PutEmailsMove):
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


@router.delete('/messages',
            response_model=Emails_delete_desponse_model,
            description='Delete email message.')
def delete_message(Request: DeleteEmails):
    request_json = Request.dict()
    mail = email(
        login      = request_json['login'],
        password   = request_json['password'],
        smtp_server= request_json['smtp_server'],
        imap_server= request_json['imap_server']
        )
    response = mail.delete_email(
        mailbox=request_json['mailbox'],
        uid=request_json['uid'],
    )
    return response


@router.put('/messages',
            response_model=Send_post_response_model,
            description='Reply email message.')
def reply_message(Request:PutReplyEmails):
    request_json = Request.dict()
    mail = email(
        login      = request_json['login'],
        password   = request_json['password'],
        smtp_server= request_json['smtp_server'],
        imap_server= request_json['imap_server']
        )
    response = {"errors": mail.reply_email(
                            mailbox     = request_json['mailbox'],
                            uid         = request_json['uid'],
                            sender      = request_json['sender'],
                            body        = request_json['body'],
                            body_type   = request_json['body_type'],
                            attachments = request_json['attachments']
                            )
                    }
    return response

@router.post('/messages/forward',
            response_model=Send_post_response_model,
            description='Forward email message.')
def forward_message(Request:PostForwardMessages):
    request_json = Request.dict()
    mail = email(
        login      = request_json['login'],
        password   = request_json['password'],
        smtp_server= request_json['smtp_server'],
        imap_server= request_json['imap_server']
        )
    response = {"errors": mail.forward(
                            mailbox     = request_json['mailbox'],
                            uid         = request_json['uid'],
                            sender      = request_json['sender'],
                            recipients  = request_json['recipients']
                            )
                    }
    return response


@router.post('/mailboxes',
             response_model= MailboxPut_response_model, 
             description="Create mailbox."
    )
def create_mailbox(Request: postMailboxCreate):
    request_json = Request.dict()
    mail = email(
        login       =request_json['login'],
        password    =request_json['password'],
        smtp_server =request_json['smtp_server'],
        imap_server =request_json['imap_server']
        )
    response = {"response": mail.mailbox_create(request_json['new_mailbox'])}
    return response


@router.delete('/mailboxes',
             response_model= MailboxPut_response_model, 
             description="Delete mailbox."
    )
def delete_mailbox(Request: deleteMailboxDelete):
    request_json = Request.dict()
    mail = email(
        login       =request_json['login'],
        password    =request_json['password'],
        smtp_server =request_json['smtp_server'],
        imap_server =request_json['imap_server']
        )
    response = {"response": mail.mailbox_delete(request_json['mailbox'])}
    return response


@router.put('/mailboxes',
             response_model= MailboxPut_response_model, 
             description="Rename mailbox."
    )
def rename_mailbox(Request: putMailboxRename):
    request_json = Request.dict()
    mail = email(
        login       =request_json['login'],
        password    =request_json['password'],
        smtp_server =request_json['smtp_server'],
        imap_server =request_json['imap_server']
        )
    response = {"response": mail.mailbox_rename(
                        request_json['old_mailbox'],request_json['new_mailbox'])}
    return response
