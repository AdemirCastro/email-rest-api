from pydantic import BaseModel, Field
from typing import Optional, NewType, Dict, List

class Anexo(BaseModel):
    encoding: str = Field(...,
                        description="Protocol used to decode file bytes to string."
                        )
    file    : str = Field(...,
                        description="File bytes converted to string.")

Filename = NewType("filename_with_extension",str)
class Anexos(BaseModel):
    __root__: Dict[Filename, Anexo]

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
    

class Email(EmailCredentials):

    sender       : str = Field(..., 
                        description="Sender name that will appear on the message, "
                                    "satisfying provider policy."
                        )

    recipients   : str = Field(..., 
                        description="String containing the recipients email addresses, "
                                    "separated by comma."
                        )
    
    Cc           : Optional[str] = Field(default=None,
                        description="Cc email list."
                        )

    subject      : str = Field(..., 
                        description="Email subject."
                        )

    body         : str = Field(..., 
                        description="Email body."
                        )

    body_type    : Optional[str] = Field(default='plain',
                        description="Type of the body content structure. For exemple, you can"
                                    " choose 'plain' for plain text content."  
                                    " If the content has html format, then you choose 'html'."
                        )

    attachments  : Optional[Anexos] = Field(default=None, 
                        description="""
    Dictionary containing email attachments.
    The dictionary must have this structure: 
    {
    'file name with extension': {
        'encoding': 
            'Protocol used to decode file bytes to string', 
        'file'    : 
            'File bytes converted to string'
        }
    }.
                        """
                        )


class send_post_response_model(BaseModel):
    errors: dict[str, tuple[int, bytes]]

class mailboxes_get_response_model(BaseModel):
    mailboxes: List[str]