import io
import re
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from core.anti_detect import AntiDetectEngine

class ContentGenerator:
    @staticmethod
    def plain_to_html(plain_text: str, custom_style: str = "") -> str:
        """
        Converts plain text input into clean, high-deliverability HTML email format.
        Preserves line breaks, links, and formats paragraphs cleanly.
        """
        if not plain_text:
            return ""
            
        # Convert URLs to clickable links if present
        def url_replacer(match):
            url = match.group(0)
            return f'<a href="{url}" style="color: #0066cc; text-decoration: underline;">{url}</a>'
            
        text_with_links = re.sub(r'https?://[^\s<>"]+|www\.[^\s<>"]+', url_replacer, plain_text)
        
        # Replace newlines with <br>
        formatted_body = text_with_links.replace('\r\n', '<br>').replace('\n', '<br>')
        
        html_template = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 14px; line-height: 1.6; color: #1a202c; }}
  .email-container {{ max-width: 600px; margin: 15px auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 6px; background-color: #ffffff; }}
  .footer {{ margin-top: 25px; padding-top: 15px; border-top: 1px solid #edf2f7; font-size: 11px; color: #718096; }}
</style>
</head>
<body>
<div class="email-container">
  <div>{formatted_body}</div>
</div>
</body>
</html>"""
        return html_template

    @staticmethod
    def create_pdf_from_content(title: str, content: str, page_format: str = 'A4') -> bytes:
        buffer = io.BytesIO()
        pagesize = A4 if str(page_format).upper() == 'A4' else letter
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=pagesize,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )
        
        styles = getSampleStyleSheet()
        normal_style = styles['Normal']
        normal_style.fontSize = 11
        normal_style.leading = 14
        
        heading_style = styles['Heading1']
        heading_style.fontSize = 16
        heading_style.leading = 20
        heading_style.textColor = '#1a365d'
        
        story = []
        if title:
            clean_title = re.sub(r'<[^>]+>', ' ', title)
            story.append(Paragraph(clean_title, heading_style))
            story.append(Spacer(1, 15))
            
        lines = content.split('\n')
        for line in lines:
            clean_line = line.strip()
            if not clean_line:
                story.append(Spacer(1, 8))
                continue
            safe_text = re.sub(r'<[^>]+>', ' ', clean_line)
            safe_text = safe_text.replace('&nbsp;', ' ').strip()
            if safe_text:
                story.append(Paragraph(safe_text, normal_style))
                story.append(Spacer(1, 4))
                
        try:
            doc.build(story)
            pdf_data = buffer.getvalue()
        except Exception:
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=pagesize)
            p.setFont('Helvetica', 12)
            y = 750
            if title:
                p.setFont('Helvetica-Bold', 14)
                p.drawString(50, y, title[:60])
                y -= 30
                p.setFont('Helvetica', 11)
            for line in lines[:50]:
                clean_l = re.sub(r'<[^>]+>', ' ', line).strip()
                if clean_l:
                    p.drawString(50, y, clean_l[:80])
                    y -= 18
                if y < 50:
                    break
            p.showPage()
            p.save()
            pdf_data = buffer.getvalue()
            
        buffer.close()
        return pdf_data

    @staticmethod
    def build_email_message(sender_email: str, sender_name: str, recipient_email: str,
                            subject: str, body_text: str, html_content: str = '',
                            output_mode: str = 'Inline Html', page_format: str = 'A4',
                            unsubscribe_link: bool = False, country: str = 'USA',
                            enable_anti_detect: bool = True) -> MIMEMultipart:
        msg = MIMEMultipart('mixed')
        
        # Anti-Detect Headers
        if enable_anti_detect:
            sender_domain = sender_email.split('@')[1] if '@' in sender_email else 'gmail.com'
            msg['Message-ID'] = AntiDetectEngine.generate_message_id(sender_domain)
            msg['X-Mailer'] = AntiDetectEngine.get_random_client_header()
            msg['User-Agent'] = AntiDetectEngine.get_random_client_header()

        if sender_name:
            msg['From'] = f'{sender_name} <{sender_email}>'
        else:
            msg['From'] = sender_email
            
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        unsub_html = ''
        unsub_text = ''
        if unsubscribe_link:
            unsub_html = "<div style='margin-top:25px; font-size:11px; color:#888;'>Click <a href='#'>here</a> to unsubscribe.</div>"
            unsub_text = "\n\nTo unsubscribe, reply with UNSUBSCRIBE in the subject."

        msg_alternative = MIMEMultipart('alternative')
        msg.attach(msg_alternative)

        # 1. Plain text alternative
        plain_body = (body_text or '') + unsub_text
        if plain_body.strip():
            msg_alternative.attach(MIMEText(plain_body, 'plain', 'utf-8'))

        # 2. ALWAYS generate rich HTML version from plain body or HTML content
        if html_content and html_content.strip() and '<' in html_content:
            final_html = html_content + unsub_html
        else:
            # Convert plain body text into styled HTML automatically!
            final_html = ContentGenerator.plain_to_html(body_text)

        # Attach HTML
        msg_alternative.attach(MIMEText(final_html, 'html', 'utf-8'))

        # Handle PDF attachment if requested in output mode
        if output_mode in ('Raw pdf', 'To pdf'):
            pdf_bytes = ContentGenerator.create_pdf_from_content(subject, body_text or html_content, page_format)
            pdf_attachment = MIMEApplication(pdf_bytes, _subtype='pdf')
            clean_sub = re.sub(r'[^a-zA-Z0-9_-]', '_', subject)[:25] or 'Document'
            filename = f'{clean_sub}.pdf'
            pdf_attachment.add_header('Content-Disposition', 'attachment', filename=filename)
            msg.attach(pdf_attachment)

        return msg
