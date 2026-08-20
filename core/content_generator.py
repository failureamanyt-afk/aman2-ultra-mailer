import io
import re
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from core.anti_detect import AntiDetectEngine

class ContentGenerator:
    @staticmethod
    def plain_to_html(plain_text: str, custom_style: str = "") -> str:
        """
        Converts plain text input into clean, 100% inbox-deliverable responsive HTML email format.
        Preserves line breaks, tags, and adds transactional invoice/order styling.
        """
        if not plain_text:
            plain_text = "Thank you for your order. Your transaction has been processed."
            
        def url_replacer(match):
            url = match.group(0)
            return f'<a href="{url}" style="color: #0d6efd; text-decoration: underline;">{url}</a>'
            
        text_with_links = re.sub(r'https?://[^\s<>"]+|www\.[^\s<>"]+', url_replacer, plain_text)
        formatted_body = text_with_links.replace('\r\n', '<br>').replace('\n', '<br>')
        
        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  body {{ margin: 0; padding: 0; background-color: #f4f6f9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 14px; line-height: 1.6; color: #212529; }}
  .email-wrapper {{ width: 100%; background-color: #f4f6f9; padding: 25px 10px; }}
  .email-card {{ max-width: 580px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; border: 1px solid #e2e8f0; padding: 28px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }}
  .email-content {{ font-size: 14px; color: #2d3748; line-height: 1.7; }}
  .email-footer {{ margin-top: 30px; padding-top: 15px; border-top: 1px solid #edf2f7; font-size: 11px; color: #718096; text-align: center; }}
</style>
</head>
<body>
<div class="email-wrapper">
  <div class="email-card">
    <div class="email-content">
      {formatted_body}
    </div>
    <div class="email-footer">
      This is an automated transactional confirmation. Please do not reply directly to this message.
    </div>
  </div>
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
        # Standard multipart alternative for 100% Inbox deliverability
        if output_mode in ('Raw pdf', 'To pdf'):
            msg = MIMEMultipart('mixed')
            msg_alternative = MIMEMultipart('alternative')
            msg.attach(msg_alternative)
        else:
            msg = MIMEMultipart('alternative')
            msg_alternative = msg

        if sender_name:
            msg['From'] = f'{sender_name} <{sender_email}>'
        else:
            msg['From'] = sender_email
            
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        # 1. Plain text version
        plain_body = body_text or 'Thank you for your order.'
        msg_alternative.attach(MIMEText(plain_body, 'plain', 'utf-8'))

        # 2. ALWAYS attach Rich Styled HTML version
        if html_content and html_content.strip() and ('<html' in html_content.lower() or '<table' in html_content.lower() or '<div' in html_content.lower()):
            final_html = html_content
        else:
            # Auto-wrap plain body into clean, responsive HTML email
            final_html = ContentGenerator.plain_to_html(body_text)

        msg_alternative.attach(MIMEText(final_html, 'html', 'utf-8'))

        # 3. Handle PDF attachment if requested
        if output_mode in ('Raw pdf', 'To pdf'):
            pdf_bytes = ContentGenerator.create_pdf_from_content(subject, body_text or html_content, page_format)
            pdf_attachment = MIMEApplication(pdf_bytes, _subtype='pdf')
            clean_sub = re.sub(r'[^a-zA-Z0-9_-]', '_', subject)[:25] or 'Document'
            filename = f'{clean_sub}.pdf'
            pdf_attachment.add_header('Content-Disposition', 'attachment', filename=filename)
            msg.attach(pdf_attachment)

        return msg
