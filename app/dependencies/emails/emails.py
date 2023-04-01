from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders, message_from_bytes
from typing import Optional, Dict, List
import smtplib
import imaplib
import re

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
            json containing email attachments.
            The json must have this structure: 
            [
                {
                    'filename': 'file name with extension'
                    'encoding': 'Protocol used to decode file bytes to string', 
                    'file'    : 'File bytes converted to string'
                }
            ].

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
    
    def get_emails_uids(self, mailbox: str, criterias_dict: Dict[str,str]) -> List[str]:
        """ Get email UIDs, given mailbox and criterias dict

        Parameters:
        -----------
        mailbox: str
            Mailbox string
        criterias_dict: Dict[str,str]
            Dict with search criterias as specified in RFC 3501 (https://www.rfc-editor.org/rfc/rfc3501#section-6.4.4).
            You must put the criteria keys as the dictionary keys, end the key parameter as the values.
        
        Return:
        -------
        email_ids: List[str]
            List containing emails UIDs corresponding to given criterias.
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
        criterias = ' '.join([' '.join([key,criterias_dict[key]]) for key in criterias_dict.keys()])
        email_ids = imap.search(None,criterias)[1][0].decode('utf-8').split()
        return email_ids
    
    def get_email(self, uid: str, mailbox: str) -> dict:
        """ Get emails, given mailbox and emails UIDs.

        Parameters:
        -----------
        uids: str
            Email uid.
        mailbox:
            Mailbox string.
        
        Return:
            emails_json: dict
                Json containing email message contents.
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
    
        data = imap.fetch(uid, 'RFC822')[1][0][1]
        email_message = message_from_bytes(data)        
        email_json: dict = {}
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
        return email_json
    
    def move_email(self, from_box: str, uid: str, to_box: str) -> Dict:
        """ Move email message from one mailbox to another.

        Parameters:
        -----------
        from_box: str
            Mailbox of the message to be moved.
        uid: str
            Uid of the message to be moved.
        to_box: str
            Destination mailbox.

        Return:
        -------
        response: dict
            Dictionary containing the move and delete operations reponses.
        """
        imap = imaplib.IMAP4_SSL(
            host= self.imap_server['host'],
            port=int(self.imap_server['port'])
            )
        imap.login(
            user    =self.login,
            password=self.password
            )
        imap.select(from_box)

        copy_response = imap.copy(uid, to_box)
        delete_response = imap.store(uid, '+FLAGS', '\\Deleted')
        imap.expunge()

        response = {
            'copy_response'  : copy_response[0],
            'delete_response': delete_response[0]
        }
        return response
    
    def delete_email(self, mailbox: str, uid: str) -> dict[str, tuple[int, bytes]]:
        """ Move email message from one mailbox to another.

        Parameters:
        -----------
        mailbox: str
            Mailbox of the message to be deleted.
        uid: str
            Uid of the message to deleted.

        Return:
        -------
        response: dict
            Dictionary containing the delete operation reponse.
        """
        imap = imaplib.IMAP4_SSL(
            host= self.imap_server['host'],
            port=int(self.imap_server['port'])
            )
        imap.login(
            user    =self.login,
            password=self.password
            )
        imap.select(mailbox)

        delete_response = imap.store(uid, '+FLAGS', '\\Deleted')
        imap.expunge()

        response = {
            'delete_response': delete_response[0]
        }
        return response
    
    def reply_email(self, mailbox: str, uid: str, sender: str, body: str, 
            body_type: str, attachments: List[Dict[str,str]]) -> dict[str, tuple[int, bytes]]:
        
        """ Reply email message.

        mailbox: str
            Mailbox of the message to be replied.
        uid: str
            Uid of the message to be replied.
        sender: str
            Sender name that will appear on the message, satisfying provider policy.
        body:
            Email message body.
        body_type: str
            Type of the body content structure. For exemple, you can choose 'plain' for plain text content.  
            If the content has html format, then you choose 'html'.
        
        """
        smtp = smtplib.SMTP(
                    host=self.smtp_server['host'], 
                    port=int(self.smtp_server['port'])
                    )
        smtp.starttls()
        smtp.login(self.login,self.password)
        imap = imaplib.IMAP4_SSL(
            host= self.imap_server['host'],
            port=int( self.imap_server['port'])
            )
        imap.login(
            user    =self.login,
            password=self.password
            )
        imap.select(mailbox)

        data = imap.fetch(uid, 'RFC822')[1][0][1]
        email_message = message_from_bytes(data)        
        msg = MIMEMultipart('mixed')
        _body = MIMEMultipart('alternative')

        headers: dict = {}
        headers['From']   = sender
        headers['To']     = email_message['To']
        headers['Cc']     = email_message['Cc']
        for key in headers:
            value = headers[key]
            if isinstance(value,list):
                value = ', '.join(value)
            msg.add_header(key,value)

        if email_message is not None:
            msg['Subject'] = "RE: "+email_message['Subject'].replace("Re: ", "").replace("RE: ", "")
            msg['In-Reply-To'] = email_message['Message-ID']
            msg['References'] = email_message['Message-ID']
            msg['Thread-Topic'] = email_message['Thread-Topic']
            msg['Thread-Index'] = email_message['Thread-Index']
        if attachments is not None:
                    for attachment in attachments:
                        att = MIMEBase('application','octet-stream')
                        file = bytes(attachment['file'], encoding=attachment['encoding'])
                        att.set_payload(file)
                        encoders.encode_base64(att)
                        att.add_header('Content-Disposition',f'attachment; filename= {attachment["filename"]}')
                        msg.attach(att)
        _body.attach(MIMEText(body, body_type))
        msg.attach(_body)
        return smtp.sendmail(msg['From'],[msg['To']],msg.as_string())
    
    def forward(self, mailbox: str, uid: str, recipients: str, 
                sender: str) -> dict[str, tuple[int, bytes]]:
        """ Forward email message.

        Parameters:
        -----------
        mailbox: str
            Mailbox of the email message to be forwarded.
        uid: str
            Uid of the email message to be forwarded.
        to: str
            String containing recipiends email addresses, separated bi comma.
        sender: str
            Sender name that will appear on the message, satisfying provider policy.
        """
        smtp = smtplib.SMTP(
                    host=self.smtp_server['host'], 
                    port=int(self.smtp_server['port'])
                    )
        smtp.starttls()
        smtp.login(self.login,self.password)
        imap = imaplib.IMAP4_SSL(
            host= self.imap_server['host'],
            port=int(self.imap_server['port'])
            )
        imap.login(
            user    =self.login,
            password=self.password
            )
        imap.select(mailbox)

        data = imap.fetch(uid, 'RFC822')[1][0][1]
        msg = message_from_bytes(data)        

        msg.replace_header('From',sender)
        msg.replace_header('To',recipients)
        msg.replace_header('Subject','Forwarded: '+msg['Subject']\
                           .replace('FWD: ','').replace('Fwd: ',''))
        return smtp.sendmail(msg['From'],[msg['To']],msg.as_string())
    
    def mailbox_create(self, new_mailbox: str) -> list:
        """ Create mailbox.

        Parameters:
        -----------
        new_mailbox: str
            Mailbox complete path.
        
        Return:
        -------
        _CommandResults:
            Imaplib create response.
        """
        smtp = smtplib.SMTP(
                    host=self.smtp_server['host'], 
                    port=int(self.smtp_server['port'])
                    )
        smtp.starttls()
        smtp.login(self.login,self.password)
        imap = imaplib.IMAP4_SSL(
            host= self.imap_server['host'],
            port=int( self.imap_server['port'])
            )
        imap.login(
            user    =self.login,
            password=self.password
            )
        return imap.create(new_mailbox)[1]
    
    def mailbox_delete(self, mailbox: str) -> list:
        """ Delete mailbox.

        Parameters:
        -----------
        mailbox: str
            Mailbox complete path.
        
        Return:
        -------
        _CommandResults:
            Imaplib delete response.
        """
        smtp = smtplib.SMTP(
                    host=self.smtp_server['host'], 
                    port=int(self.smtp_server['port'])
                    )
        smtp.starttls()
        smtp.login(self.login,self.password)
        imap = imaplib.IMAP4_SSL(
            host= self.imap_server['host'],
            port=int( self.imap_server['port'])
            )
        imap.login(
            user    =self.login,
            password=self.password
            )
        return imap.delete(mailbox)[1]
    
    def mailbox_rename(self, old_mailbox: str, new_mailbox: str) -> list:
        """ Create mailbox.

        Parameters:
        -----------
        old_mailbox: str
            Old mailbox complete path.
        new_mailbox: str
            New mailbox name.
        
        Return:
        -------
        _CommandResults:
            Imaplib rename response.
        """
        smtp = smtplib.SMTP(
                    host=self.smtp_server['host'], 
                    port=int(self.smtp_server['port'])
                    )
        smtp.starttls()
        smtp.login(self.login,self.password)
        imap = imaplib.IMAP4_SSL(
            host= self.imap_server['host'],
            port=int( self.imap_server['port'])
            )
        imap.login(
            user    =self.login,
            password=self.password
            )
        return imap.rename(old_mailbox, new_mailbox)[1]