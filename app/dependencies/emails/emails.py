from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from typing import Optional, Dict, List
import smtplib
import imaplib

class email:
    """
    Class for email operations.    
    """

    def __init__(self, login: str, password: str, 
                smtp_server: Dict[str,str], imap_server: Dict[str,str]) -> None:
        """
        Parameters:
        -----------
        login: str
            "Email account login in a email provider."
        password: str
            "Application password for the email account."
        smtp_server: str
            "Address and port of the SMTP server from email provider."
        imap_server: str
            "Address and port of the IMAP server from email provider."

        Return:
        -------
        None
        """
        self.login       = login
        self.password    = password
        self.smtp_server = smtp_server
        self.imap_server = imap_server

    def send_email( self,
                    sender: str, recipients: str, Cc: Optional[str], subject: str, 
                    body: str, attachments: Optional[dict], body_type: str= 'plain'
                ) -> dict[str, tuple[int, bytes]]:
        """ Send a email.
        
        Parameters:
        -----------
        sender: str
            Sender name that will appear on the message, satisfying provider policy.
        recipients: str
            String containing the recipients email addresses, separated by comma.
        Cc: Optional[str]
            Cc email list, separated by comma.
        subject: str
            Email subject.
        body: str
            Email body.
        body_type: str
            Type of the body content structure. For exemple, you can choose 'plain' for plain text content.  
            If the content has html format, then you choose 'html'.
        attachments: Optional[dict]
            Dictionary containing email attachments.
            The dictionary must have this structure: 
            {
                'file name with extension': {
                    'encoding': 'Protocol used to decode file bytes to string', 
                    'file'    : 'File bytes converted to string'
                    }
                }.

        Return:
        --------
        _SendErrs
        """
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From']    = sender
        msg['Cc']      = Cc
        msg['To']      = recipients
        msg.add_header('Content-Type', body_type)
        msg.attach(MIMEText(body, body_type))

        if attachments is not None:
            for attachment_name in attachments:
                att = MIMEBase('application','octet-stream')
                attachment = attachments[attachment_name]
                file = bytes(attachment['file'], encoding=attachment['encoding'])
                att.set_payload(file)
                encoders.encode_base64(att)
                att.add_header('Content-Disposition',f'attachment; filename= {attachment_name}')
                msg.attach(att)
        smtp = smtplib.SMTP(
            host=self.smtp_server['host'], 
            port=int(self.smtp_server['port'])
            )
        smtp.starttls()

        smtp.login(self.login,self.password)
        return smtp.sendmail(msg['From'],[msg['To']],msg.as_string())
    
    def get_mailboxes(self) -> List[str]:
        
        mail = email(
        login       =self.login,
        password    =self.password,
        smtp_server =self.smtp_server,
        imap_server =self.imap_server
        )

        imap = imaplib.IMAP4_SSL(
        host=mail.imap_server['host'],
        port=int(mail.imap_server['port'])
        )
        
        imap.login(
            user    =mail.login,
            password=mail.password
            )
        mailboxes = [item.decode('utf-8').split(r' "/" ')[1].replace(r'"','') 
                                                for item in imap.list()[1]]
        return mailboxes