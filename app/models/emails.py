from pydantic import BaseModel, Field
from typing import Optional, NewType, Dict, List

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
                        description="Cc email list."
                        )

    subject     : str = Field(..., 
                        description="Email subject."
                        )

    body        : str = Field(..., 
                        description="Email body."
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
    Uid        : str = Field(..., description='Email message Uid.')
    Subject    : str = Field(..., description='Email message subject.')
    Date       : str = Field(..., description='Email message received date.')
    From       : _From = Field(..., description='Email message "From" field.')
    Body       : List[EmailContent] = Field(..., description='Email message body contents.')
    attachments: List[Attachment] = Field(..., description='Email message attachments.')

class EmailUIDs(EmailCredentials):
    mailbox: str = Field(...,description='Mailbox string.')
    uids   : List[str] = Field(...,description='List of emails UIDs.')

class GetEmailsUIDsForm(EmailCredentials):
    mailbox: str = Field(..., description='Mailbox string.')
    criterias: Dict[str,str] = Field(..., description="""
        Dict with search criterias as specified in RFC 3501 (https://www.rfc-editor.org/rfc/rfc3501#section-6.4.4).
        You must put the criteria keys as the dictionary keys, end the key parameter as the values.
    """)

class send_post_response_model(BaseModel):
    errors: dict[str, tuple[int, bytes]]

class mailboxes_get_response_model(BaseModel):
    mailboxes: List[str]

class getEmails_get_response_model(BaseModel):
    emails: List[EmailMessage]

class getUIDs_get_response_model(BaseModel):
    uids: List[str]
