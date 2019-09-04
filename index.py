import flask, os,sys,time,re, urllib.parse
from webPanLib import *
from flask import request, send_from_directory,redirect,url_for

interface_path = os.path.dirname(__file__)
sys.path.insert(0, interface_path)  #将当前文件的父目录加入临时系统变量


server = flask.Flask(__name__)


#get方法：指定目录下载文件
@server.route('/download', methods=['get'])
def download():
    fpath = request.values.get('path', '') #获取文件路径
    fname = request.values.get('filename', '')  #获取文件名
    fpathT = os.path.join(rootPath, fpath) #真实路径
    if fname.strip() and fpath.strip():
        #print(fname, fpath);
        if os.path.isfile(os.path.join(fpathT,fname)): # and os.path.isdir(fpath):
            return send_from_directory(fpathT, fname, as_attachment=True) #返回要下载的文件内容给客户端
        else:
            return '{"msg2":"参数不正确"}path=%s, filename=%s;' %(fpathT, fname);
    else:
        return '{"msg1":"请输入参数"}'
#

@server.route('/', methods=['get'])
def index():
    return redirect("/list");
#



# get方法：查询当前路径下的所有文件
@server.route('/list', methods=['get'])
def getfiles():
    debug='';
    
    fpath = request.values.get('fpath', './') #获取用户输入的目录
    #保护目录，保证只能传入相对路径
    if not fpath.startswith("."):
        if fpath.startswith("/"):
            fpath='.'+fpath;
        else:
            fpath='./'+fpath;
    fpathT=os.path.join(rootPath, fpath); #真实地址
    debug+="<div id=fpath style='display:none;'>"+fpath+"</div>";
    #生成顶部路径超链接
    #str to arr, by the end of path
    sep=fpathT[-1];
    arr=re.split(sep, fpath);
    #arr to a links
    url="/list?fpath="
    urlPath="<a href=/list>(RootDir)</a>/";
    for i in range(len(arr)-1 ):
        if arr[i]=='.':
            continue;
        if i<len(arr)-2:
            url=url+ arr[i]+"/";
            urlPath+="<a href="+url+">"+arr[i]+"</a>/"
        else:
            urlPath+=arr[i]+"/";
        #print(i, arr[i], urlPath)
    titlePath="<h4 class=root>Index of "+urlPath+"</h4>\n\n"; #cut to pieces.

    #返回上一级的url链接和tr
    htmlBack="";
    if fpath!="./":
        arr=re.split('/',fpath);
        urlBack="/".join(arr[:-2])+"/";
        htmlBack="<tr> <td>"+img['back']+" <a title='点击返回上一级' href='/list?fpath="+urlBack+"'>..</a>"+"</td>  <td></td>  <td></td> <tr>\n"
    #tr 文件和文件夹
    htmlF="";
    htmlD="";
    table1="<table><tr> <th>FileName</th>   <th>Size</th>   <th>Modified</th>  </tr>\n"
    if os.path.isdir(fpathT):
        filelist = os.listdir(fpathT)
        for i in range(len(filelist)):
            file=filelist[i];
            url=os.path.join(fpath, file); #显示用虚拟文件路径
            urlT=os.path.join(fpathT, file); #获取都要用真实路径
            fTime=getModifiedTime(urlT);#真实路径获取时间
            #
            if os.path.isfile(urlT): #type="file"
                fSize=getDocSize(urlT);
                htmlF+="<tr class=file><td>"+img['file']+" <a title='点击下载' target='_blank' href='/download?filename="+file+"&path="+fpath+"'>"+file+"</a></td>  <td>"+fSize+"</td>   <td>"+fTime+"</td>  </tr>\n"
            if os.path.isdir(urlT): #type="dir"
                htmlD+="<tr class=dir><td>"+img['dir']+" <a title='点击打开' href='/list?fpath="+url+"/'>"+file+"/</a></td> <td>-</td>  <td>"+fTime+"</td>  </tr>\n"
        #files = [file for file in filelist if os.path.isfile(os.path.join(fpath, file))]
    return head+debug+"<hr>"+titlePath+table1+htmlBack+htmlF+htmlD+"</table>";


# post方法：上传文件的 https://www.cnblogs.com/wl443587/p/10552542.html
@server.route('/upload', methods=['POST'])
def upload():
    fname = request.files.get('file')  #获取上传的文件
    uploadDir = request.form['uploadDir'] #获取上传的路径
    uploadDir = request.form.get('uploadDir','./') #获取上传的路径
    #return uploadDir;
    
    if fname:
        t = time.strftime('%Y%m%d%H%M%S')
        new_fname = os.path.join(rootPath, uploadDir, t +'_'+ fname.filename);
        fname.save(new_fname)  #保存文件到指定路径
        url=url_for('getfiles',fpath=uploadDir );
        #return url;
        return '<meta http-equiv="refresh" content="3;url='+url+'">'+"Upload Success!. Returning to list in 3 seconds.<br>";
    else:
        return '{"msg": "请上传文件！"}'



# 添加新静态文件的路径，这样就允许xx/下的图片加载了
@server.route("/static/<path:filename>")
def downloader(filename):
    return send_from_directory("static",filename,as_attachment=False)



# run the app
if __name__ == '__main__':
    server.debug = True # 设置调试模式，生产模式的时候要关掉debug
    server.run(host="127.0.0.1",port=8005) #default