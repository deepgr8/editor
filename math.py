from flask import Flask
from flask_restful import Resource, Api, reqparse
from rpa_pdf import Pdf

app = Flask(__name__)
api = Api(app)
pdf = Pdf()

class MergePDFs(Resource):
    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('pdf_files', type=list, required=True, help='List of PDF files to merge', location='json')
            parser.add_argument('output_filename', type=str, default='merged.pdf', help='Output filename for merged PDF', location='json')
            args = parser.parse_args()

            print(args)  # Add this line for debugging

            pdf_files = args['pdf_files']

            if len(pdf_files) < 2:
                return {'error': 'At least two PDF files are required for merging.'}, 400

            output_filename = args['output_filename']

            pdf.merge(pdf_files, output_filename)

            return {'message': 'PDFs merged successfully!', 'merged_pdf': output_filename}

        except Exception as e:
            return {'error': str(e)}, 500


api.add_resource(MergePDFs, '/merge_pdfs')

if __name__ == '__main__':
    app.run(debug=True)
