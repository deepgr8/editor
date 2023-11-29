from flask import Flask,jsonify,json ,flash, render_template,redirect,url_for,request,send_from_directory,send_file
import docx2pdf
import tempfile
import pythoncom
import os
from PyPDF2 import PdfReader, PdfWriter,PaperSize
from flask_restful import Api, Resource
from pdf2docx import Converter,parse

app = Flask(__name__)
api = Api(app)
app.config['UPLOAD_FOLDER']='uploads'
app.secret_key = "LEapdf8sdufhbcsjkbh34586"

@app.route('/')
def index():
    return render_template('index.html')
def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

class merging(Resource):
    def post(self):
        pythoncom.CoInitialize()
        f = request.files
class ResizePDF(Resource):
    def post(self):
        try:
            # Get parameters from the request
            page_size = request.form.get('page_size', 'A4')
            file = request.files['file']

            # Process PDF
            pdf_reader = PdfReader(file)
            original_page = pdf_reader._get_page(0)

            # Set dimensions based on page size
            if page_size == "A4":
                    newWidth, newHeight = PaperSize.A4.width, PaperSize.A4.height
            elif page_size == "A5":
                    newWidth, newHeight = PaperSize.A5.width, PaperSize.A5.height
            elif page_size == "A3":
                    newWidth, newHeight = PaperSize.A3.width, PaperSize.A3.height
            else:
                raise ValueError("Invalid page size specified")

            # Scale the copied page
            original_page.scale_to(newWidth, newHeight)

            # Write the resized PDF to a new file
            pdf_writer = PdfWriter()
            pdf_writer.add_page(original_page)
            output_path = '/resized_output.pdf'
            with open(output_path, 'wb+') as output_file:
                pdf_writer.write(output_file)

            return send_file(output_path, as_attachment=True)

        except Exception as e:
            return {'error': str(e)}

class WordToPdfResource(Resource):
    def post(self):
        pythoncom.CoInitialize()
        f = request.files['file']
        if f and allowed_file(f.filename, {'doc', 'docx'}):
            file_name, file_extension = os.path.splitext(f.filename)
            pdf_file_name = file_name + '.pdf'
            tmp_dir = tempfile.mkdtemp()
            uploaded_file_path = os.path.join(tmp_dir, f.filename)
            f.save(uploaded_file_path)
            pdf_file_path = os.path.join(tmp_dir, pdf_file_name)

            docx2pdf.convert(uploaded_file_path, pdf_file_path)
            
            response_data = {
                "message": "Conversion successful",
                "pdf_url": pdf_file_path
            }
            return json.dumps(response_data, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

class PdfToWordResource(Resource):
    def post(self):
        f = request.files['pdffile']
        if f and allowed_file(f.filename, {'pdf'}):
            file = f.filename
            tmp_dir = tempfile.mkdtemp()
            uploaded_file_path = os.path.join(tmp_dir, file)
            f.save(uploaded_file_path)
            word_file_path = uploaded_file_path + '.docx'
            cv = Converter(uploaded_file_path)
            cv.convert(word_file_path, start=0, end=None)
            response_data = {
                "message": "Conversion successful",
                "pdf_url": word_file_path
            }
            return json.dumps(response_data,200)
        # else:
        #     # Construct an error response
        #     error_data = {
        #         "error": "Invalid file format. Please upload a .doc or .docx file."
        #     }
            
        #     return jsonify(error_data), 400

api.add_resource(WordToPdfResource, '/AndroidWordTopdf')
api.add_resource(PdfToWordResource, '/Androidpdftoword')
api.add_resource(ResizePDF, '/resize-pdf')

@app.route('/compressPdf',methods=['POST','GET'])
def compressPdf():
    from PyPDF2 import PdfReader,PdfWriter
    if request.method=='POST':
        files = request.files['pdf_file']
        if files.name=='':
            flash("No selected files")
            return render_template("compress preview.html")
        else:
            tmpdirc = tempfile.mkdtemp()
            file_path = os.path.join(tmpdirc,files.name)
            files.save(file_path)
            reader = PdfReader(file_path)
            writer = PdfWriter()
            for page in reader.pages:
                compressed_content_streams = []
                for content_stream in page.compressContentStreams:
                    compressed_content_streams.append(content_stream.compress())
                page.content_streams = compressed_content_streams
                writer.add_page(page)

            compressed_file_name = f"compressed{files.name}.pdf"
            compressed_file_path = os.path.join(tmpdirc, compressed_file_name)

            with open(compressed_file_path, "wb") as f:
                writer.write(f)
                #  return render_template("downsite.html")
            return send_from_directory(tmpdirc, os.path.basename(compressed_file_path), as_attachment=True)

@app.route('/encryptPdf',methods=['POST','GET'])
def encryptpdf():
    from PyPDF2 import PdfReader,PdfWriter
    if request.method=='POST':
        files = request.files['pdf_file']
        password = request.form['password']
        if files.name=='':
            flash("No selected files")
            return render_template('protectpdf preview.html')
        else:
            tmpdirc = tempfile.mkdtemp()
            file_path = os.path.join(tmpdirc,files.name)
            files.save(file_path)
            reader = PdfReader(file_path)
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            writer.encrypt(password,use_128bit=True)
            
            encrypted_file_name = 'encrypted.pdf'
            encrypted_file_path = os.path.join(tmpdirc, encrypted_file_name)
            with open(encrypted_file_path, 'wb') as output_pdf:
                writer.write(output_pdf)
            return send_from_directory(tmpdirc, os.path.basename(encrypted_file_path), as_attachment=True)
        
@app.route('/decryptPdf',methods=['POST','GET'])
def decryptpdf():
    from PyPDF2 import PdfReader,PdfWriter
    if request.method=='POST':
        files = request.files['pdf_file']
        password = request.form['password']
        if files.name=='':
            flash("No selected files")
            return render_template('unlockpdf preview.html')
        else:
            tmpdirc = tempfile.mkdtemp()
            file_path = os.path.join(tmpdirc,files.name)
            files.save(file_path)
            reader = PdfReader(file_path)
            writer = PdfWriter()
            try:
                if reader.is_encrypted:
                    reader.decrypt(password)
                for page in reader.pages:
                    writer.add_page(page)    
                encrypted_file_name = 'decrypted.pdf'
                encrypted_file_path = os.path.join(tmpdirc, encrypted_file_name)
                with open(encrypted_file_path, 'wb') as output_pdf:
                    writer.write(output_pdf)
                return send_from_directory(tmpdirc, os.path.basename(encrypted_file_path), as_attachment=True)
            except Exception as e:
                flash("Wrong Password")
                return render_template("unlockpdf preview.html")


@app.route('/imgIntopdf', methods=['POST','GET'])
def imgIntopdf():
    import img2pdf
    if request.method =='POST':
        files = request.files['imagefile']
        if files.name=='':
            flash("No selected files")
            return render_template('JPG to pdf preview.html')
        else:
            tmpDir = tempfile.mkdtemp()
            file_path=os.path.join(tmpDir, files.name + '.pdf')
            files.save(file_path)
            pdfbytes=img2pdf.convert(file_path)
            file = open(file_path,'wb')
            file.write(pdfbytes)
            file.close
            return send_from_directory(tmpDir, os.path.basename(file_path), as_attachment=True)
        
@app.route('/PdfIntoword', methods=['POST', 'GET'])
def fileIntoword():
    if request.method =='POST':
        files = request.files['pdffile']
        if files.name=='':
            flash("No selected files")
            return render_template('pdf to word preview.html')
        else:
            tmpdir = tempfile.mkdtemp()
            file_path=os.path.join(tmpdir, files.name)
            files.save(file_path)
            word_filePath= file_path + '.docx'
            parse(file_path,word_filePath,start=0,end=None)
            return send_from_directory(tmpdir, os.path.basename(word_filePath), as_attachment=True)
    
@app.route('/wordtopdf', methods=['POST'])
def wordToPdf():
        pythoncom.CoInitialize()
        if request.method == 'POST':
            f = request.files['file']
            if f and allowed_file(f.filename):
                    file = f.filename
                    tmp_dir = tempfile.mkdtemp()
                    uploaded_file_path = os.path.join(tmp_dir, file)
                    f.save(uploaded_file_path)
                    pdf_file_path = uploaded_file_path + '.pdf'
                
                    docx2pdf.convert(uploaded_file_path, pdf_file_path)
    
                    return send_from_directory(tmp_dir, os.path.basename(pdf_file_path), as_attachment=True)
            else:
                flash("Invalid file format. Please upload a .doc or .docx file.")
                return redirect('/wordtopdf_Page')
                     
@app.route('/pdf')
def pdf():
    return render_template('word to pdf preview.html')

@app.route('/split')
def split():
         return render_template("downsite.html")
    # return render_template("split preview.html")

@app.route('/merge')
def merge():
        #  return render_template("downsite.html")
    return render_template("merge preview.html")

@app.route('/wordtopdf_Page')
def wordtopdf_Page():
    return render_template('word to pdf preview.html')

@app.route('/login')
def login():
         return render_template("downsite.html")
    # return render_template("login.html")

def loginwithGoogle():
    return redirect(url_for('index'))

def loginwithFacebook():
    return redirect(url_for('index'))

def emailLogin():
    return redirect(url_for('index'))

@app.route('/compress')
def compress():
    return render_template("compress preview.html")
# pdf to word
@app.route('/PdftoWord')
def PdftoWord():
    return render_template("pdf to word preview.html")

# pdf to powerpoint
@app.route('/Pdftopower')
def Pdftopower():
         return render_template("downsite.html")
    # return render_template("pdf to powerpoint preview.html")

# pdf to excel
@app.route('/pdfToExcel')
def pdfToExcel():
         return render_template("downsite.html")
    # return render_template("pdf to excel preview.html")

# word to pdf
@app.route('/wordtopdf')
def wordtopdf():
    return render_template("word to pdf preview.html")

# powerpoint to pdf
@app.route('/powerpointtopdf')
def powerpointtopdf():
         return render_template("downsite.html")
    # return render_template("powerpoint to pdf preview.html")

# excel to pdf
@app.route('/Exceltopdf')
def Exceltopdf():
         return render_template("downsite.html")
    # return render_template("excel to pdf preview.html")

@app.route('/editPdf')
def editPdf():
         return render_template("downsite.html")
    # return render_template("edit pdf options preview.html")

# pdf to jpg
@app.route('/pdftoJpg')
def pdftoJpg():
         return render_template("downsite.html")
    # return render_template("pdf to jpg preview.html")

# jpg to pdf
@app.route('/JPGtopdf')
def JPGtopdf():     
    return render_template("JPG to pdf preview.html")

@app.route('/sign')
def sign():
         return render_template("downsite.html")
    # return render_template("sign pdf preview.html")

@app.route('/watermark')
def watermark():
         return render_template("downsite.html")
    # return render_template("watermark preview.html")

@app.route('/rotate')
def rotate():
        return render_template("downsite.html")
    # return render_template("rotate pdf preview.html")
# html to pdf
@app.route('/htmltoPdf')
def htmltoPdf():
         return render_template("downsite.html")
    # return render_template("html to pdf preview.html")

@app.route('/unlockPDf')
def unlock_pDf():
        # return render_template("downsite.html")
    return render_template("unlockpdf preview.html")

@app.route('/protectPdf')
def protectPdf():
        # return render_template("downsite.html")
    return render_template("protectpdf preview.html")

@app.route('/organize')
def organize():
        return render_template("downsite.html")
    # return render_template("organize pdf preview.html")

def pdfa():
        return render_template("downsite.html")
    # return render_template("pdf to pdfa preview.html")

@app.route('/repair')
def repair():
        return render_template("downsite.html")
    # return render_template("Repair preview.html")

@app.route('/pageNum')
def pageNum():
        return render_template("downsite.html")
    # return render_template("pagenumberpreview.html")

@app.route('/ocr')
def ocr():
    return render_template("downsite.html")
    return render_template("ocr pdf preview.html")

# if __name__ == '__main__':
#     app.run(debug=True)
