from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders, message_from_bytes
from typing import Optional, Dict, List
import smtplib
import imaplib
import re
import base64

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
            for attachment in attachments:
                att = MIMEBase('application','octet-stream')
                file = bytes(attachment['file'], encoding=attachment['encoding'])
                att.set_payload(file)
                encoders.encode_base64(att)
                att.add_header('Content-Disposition',f'attachment; filename= {attachment["filename"]}')
                msg.attach(att)
        smtp = smtplib.SMTP(
            host=self.smtp_server['host'], 
            port=int(self.smtp_server['port'])
            )
        smtp.starttls()

        smtp.login(self.login,self.password)
        return smtp.sendmail(msg['From'],[msg['To']],msg.as_string())
    
    def get_mailboxes(self) -> List[str]:
        """ Get mailboxes.

        Parameters:
        -----------
        None

        Return:
        -------
        mailboxes: List[str]
            List containing mailboxes names.
        """

        imap = imaplib.IMAP4_SSL(
        host=self.imap_server['host'],
        port=int(self.imap_server['port'])
        )
        
        imap.login(
            user    =self.login,
            password=self.password
            )
        mailboxes = [item.decode('utf-8').split(r' "/" ')[1].replace(r'"','') 
                                                for item in imap.list()[1]]
        return mailboxes
    
    def get_emails(self, uids: List[str], mailbox: str) -> dict:
        """ Get emails, given mailbox and emails UIDs.

        Parameters:
        -----------
        uids: List[str]
            List of email uids.
        mailbox:
            Mailbox string.
        
        Return:
            emails_json: dict
                Json containing email contents by uid.
        """
        imap = imaplib.IMAP4_SSL(
            host= self.imap_server['host'],
            port=int(self.imap_server['port'])
            )
            
        imap.login(
            user    =self.login,
            password=self.password
            )
        imap.select(mailbox, readonly=True)

        emails_list: list = []
        for id in uids:
            data = imap.fetch(id, 'RFC822')[1][0][1]
            email_message = message_from_bytes(data)        
            email_json: dict = {}
            email_json['Uid']     = id
            email_json['Subject'] = email_message['Subject']
            email_json['Date']    = email_message['Date']

            try:
                from_name = re.search('"(.*)"', email_message['From']).group(1)
            except AttributeError:
                from_name = ''
            try:
                from_email= re.search('<(.*)>', email_message['From']).group(1)
            except AttributeError:
                from_email= email_message['From']
            email_json['From']    = {'name': from_name, 'email': from_email}

            attachments = []
            body: List[Dict[str,str]] = []
            if email_message.is_multipart():
                for part in email_message.walk():
                    ctype = part.get_content_type()

                    if ctype in ['text/html','text/plain']:
                        body.append({
                            'content_type': ctype,
                            'content': part.get_payload()
                                }
                            )
                    if part.get_content_maintype() != 'multipart' and part.get('Content-Disposition') is not None:
                        attachments.append({
                            'filename': '' if part.get_filename() is None else part.get_filename(),
                            'encoding': 'base64',
                            'file': part.get_payload()
                                }
                            )
            else:
                body.append({
                    'content_type': email_message.get_content_type(),
                    'content': email_message.get_payload()
                        }
                    )
                
            email_json['Body']        = body
            email_json['attachments'] = attachments

            emails_list.append(email_json)
        return emails_list