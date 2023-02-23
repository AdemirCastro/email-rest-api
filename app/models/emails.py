from pydantic import BaseModel, Field
from typing import Optional,Dict, List

class Attachment(BaseModel):
    filename: str = Field(..., 
                        description='Filename with extension.'
                        )
    encoding: str = Field(...,
                        description="Protocol used to decode file bytes to string."
                        )
    file    : str = Field(...,
                        description="File bytes converted to string."
                        )

class Server(BaseModel):
    host: str
    port: str

class EmailCredentials(BaseModel):
    login        : str = Field(..., 
                        description="Email account login in a email provider."
                        )

    password     : str = Field(..., 
                        description="Application password for the email account."
                        )

    smtp_server: Optional[Server] = Field(default={"host":"imap.gmail.com", "port":"587"},
                        description="Address and port of the SMTP server from email provider."
                        )

    imap_server: Optional[Server] = Field(default={"host":"imap.gmail.com", "port":"993"}, 
                        description="Address and port of the SMTP server from email provider."
                        )
    
class EmailSend(EmailCredentials):

    sender      : str = Field(..., 
                        description="Sender name that will appear on the message, "
                                    "satisfying provider policy."
                        )

    recipients  : str = Field(..., 
                        description="String containing the recipients email addresses, "
                                    "separated by comma."
                        )
    
    Cc          : Optional[str] = Field(default=None,
                        description="Cc email message list."
                        )

    subject     : str = Field(..., 
                        description="Email message subject."
                        )

    body        : str = Field(..., 
                        description="Email message body."
                        )

    body_type   : Optional[str] = Field(default='plain',
                        description="Type of the body content structure. For exemple, you can"
                                    " choose 'plain' for plain text content."  
                                    " If the content has html format, then you choose 'html'."
                        )

    attachments : Optional[List[Attachment]] = Field(default=None, 
                        description="""
    json containing email attachments.
    The json must have this structure: 
    [
        {
        'filename': 
            'file name with extension',
        'encoding': 
            'Protocol used to decode file bytes to string', 
        'file'    : 
            'File bytes converted to string'
        }
    ].
                        """
                        )

class _From(BaseModel):
    name : str = Field(..., description= 'Name on "from" field.')
    email: str = Field(..., description= 'Email address on "from" field.')

class EmailContent(BaseModel):
    content_type: str = Field(..., description='Content type.')
    content     : str = Field(..., description='Content.')

class EmailMessage(BaseModel):
    Subject    : str = Field(..., description='Email message subject.')
    Date       : str = Field(..., description='Email message received date.')
    From       : _From = Field(..., description='Email message "From" field.')
    Body       : List[EmailContent] = Field(..., description='Email message body contents.')
    attachments: List[Attachment] = Field(..., description='Email message attachments.')

class EmailUID(EmailCredentials):
    mailbox: str = Field(...,description='Mailbox string.')
    uid   : str = Field(...,description='Email UID.')

class GetEmailsUIDsForm(EmailCredentials):
    mailbox: str = Field(..., description='Mailbox string.')
    criterias: Dict[str,str] = Field(..., description="""
        Dict with search criterias as specified in RFC 3501 (https://www.rfc-editor.org/rfc/rfc3501#section-6.4.4).
        You must put the criteria keys as the dictionary keys, end the key parameter as the values.
    """)

class PutEmailsMove(EmailCredentials):
    from_box: str = Field(...,description='Mailbox box of the message to be moved.')
    uid     : str = Field(...,description='Uid of the message to be moved.')
    to_box  : str = Field(...,description='Destination mailbox.')

class DeleteEmails(EmailCredentials):
    mailbox: str = Field(..., description='Mailbox of the message to be deleted.')
    uid    : str = Field(..., description='Uid of the message to be moved.')

class PutReplyEmails(EmailCredentials):
    mailbox  : str = Field(..., 
                        description="Mailbox of the message to be replied."
                        )
    uid      : str = Field(..., 
                        description='Uid of the message to be replied.')
    sender   : str = Field(..., 
                        description="Sender name that will appear on the message, "
                                    "satisfying provider policy."
                        )
    body     : str = Field(..., 
                        description="Email message body.")
    body_type: Optional[str] = Field(default='plain',
                        description="Type of the body content structure. For exemple, you can"
                                    " choose 'plain' for plain text content."  
                                    " If the content has html format, then you choose 'html'."
                        )
    attachments: Optional[List[Attachment]] = Field(default=None, 
                        description="""
        json containing email attachments.
        The json must have this structure: 
        [
            {
            'filename': 
                'file name with extension',
            'encoding': 
                'Protocol used to decode file bytes to string', 
            'file'    : 
                'File bytes converted to string'
            }
        ].
                            """
                            )

class PostForwardMessages(EmailCredentials):
    mailbox   : str = Field(..., 
                        description="Mailbox of the message to be replied."
                    )
    uid       : str = Field(..., description='Uid of the message to be moved.')
    sender    : str = Field(..., 
                        description="Sender name that will appear on the message, "
                                    "satisfying provider policy."
                    )
    recipients: str = Field(..., 
                        description="String containing the recipients email addresses, "
                                    "separated by comma."
                    )
    
class postMailboxCreate(EmailCredentials):
    new_maibox: str = Field(..., description='New mailbox complete path, with name.')

class putMailboxRename(EmailCredentials):
    old_mailbox: str = Field(..., description='Old maibox path, with name.')
    new_mailbox: str = Field(..., description='New mailbox name.')

class deleteMailboxDelete(EmailCredentials):
    mailbox: str = Field(..., description=
                         'Complete path of the mailbox to be deleted, with name.')

class Send_post_response_model(BaseModel):
    errors: dict[str, tuple[int, bytes]]

class Mailboxes_get_response_model(BaseModel):
    mailboxes: List[str]

class Emails_get_response_model(BaseModel):
    emails: EmailMessage

class UIDs_get_response_model(BaseModel):
    uids: List[str]

class Move_put_desponse_model(BaseModel):
    copy_response: str
    delete_response: str

class Emails_delete_desponse_model(BaseModel):
    delete_response: str

class MailboxPut_response_model(BaseModel):
    response: list