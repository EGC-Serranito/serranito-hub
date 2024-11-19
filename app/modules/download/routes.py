from flask import render_template
from app.modules.download import download_bp


@download_bp.route('/download', methods=['GET'])
def index():
    return render_template('download/index.html')
