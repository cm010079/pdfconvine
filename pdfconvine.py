# -*- coding:utf-8 -*-
import sys
import os
import subprocess
from PyQt4 import QtGui, QtCore

url_list =[]

class DragDropItemModel( QtGui.QStandardItemModel ):
    '''ドロップ可能なQStandardItemModelの派生クラス。'''
    def __init__( self, parent=None ):
        super( DragDropItemModel, self ).__init__( 0, 3, parent )
        self.setHeaderData( 0, QtCore.Qt.Horizontal, 'File Path' )
        self.setHeaderData( 1, QtCore.Qt.Horizontal, 'Last Update' )
        self.setHeaderData( 2, QtCore.Qt.Horizontal, 'File Size' )

    def addObject( self, url ):
        '''QUrlを受け取って、リストに追加するメソッド。'''
        filepath = url.path()            # QUrlからパスを取得。

        # Windowsから送られてくるuri-listは頭に/が付いているので
        # それをはずす。
        #filepath = filepath[1:]

        # uri-listはパスの区切り文字が/なので、Windows風に￥に置き換える。
        #filepath = filepath.replace( '/', '\\' )

        # 追加するアイテムを作成。---------------------------------------------------------
        row = self.rowCount()
        # ファイルパスのアイテムの追加。
        item = QtGui.QStandardItem()
        item.setText( filepath )

        #マスターリストに追加
        url_list.append(filepath)
        self.setItem( row, 0, item )

        fileinfo = QtCore.QFileInfo( filepath )
        # ファイルの更新日時のアイテムの追加。
        item = QtGui.QStandardItem()
        item.setText( fileinfo.lastModified().toString( 'yyyy/MM/dd hh:mm:ss' ) )
        self.setItem( row, 1, item )

        # ファイルのサイズのアイテムを追加。
        item = QtGui.QStandardItem()
        item.setText(
            str( round( fileinfo.size() / 1024.0, 2 ) ) + 'KB'
        )
        self.setItem( row, 2, item )
        # ---------------------------------------------------------------------------------

class DragDropTreeView( QtGui.QTreeView ):
    '''ドラッグ＆ドロップ可能なQTreeViewの派生クラス。'''
    def __init__( self, parent=None ):
        super( DragDropTreeView, self ).__init__( parent )
        self.setDragEnabled( True )            # ドラッグ可能に設定。
        self.setAcceptDrops( True )            # ドロップ可能に設定。
        self.setSortingEnabled( True )        #  ソート可能に設定。
        # ドラッグ＆ドロップのモードを指定。
        self.setDragDropMode(
            QtGui.QAbstractItemView.InternalMove
        )

    def dragEnterEvent( self, event ):
        '''ファイルがこのビューにドラッグされてきた時の挙動を指定。'''
        # 渡されるeventオブジェクトからドラッグされたデータのmimeデータを取得。
        mimedata = event.mimeData()
        if mimedata.hasUrls():
            # ファイルのパス情報を含むmime-type(uri-list)の場合ドロップを許可する
            # 通知を送る。
            event.accept()
        else:
            # それ以外の場合はドロップを無視する通知を送る。
            event.ignore()

    def dropEvent( self, event ):
        '''dropを許可して、かつユーザーがこのビューにドロップした場合の処理'''
        mimedata = event.mimeData()

        # このTreeViewにセットされているItemModelを取得する。
        model = self.model()

        if mimedata.hasUrls():
            # QUrlListを取得すし、それをfor文で個別に処理をする。
            urllist = mimedata.urls()
            for url in urllist:
                model.addObject( url )
                #itellist[url] =url
                #print(itellist[url])
            event.accept()
        else:
            event.ignore()

class MainWindow( QtGui.QWidget ):
    def __init__( self, parent=None ):
        super( MainWindow, self ).__init__( parent )

        self.resize( 640, 480 )

        #statusBar
        self.status_bar = QtGui.QStatusBar(self)
        self.setWindowTitle('PDF CONVINE')

        #layout   = QtGui.QVBoxLayout( self )
        layout = QtGui.QVBoxLayout(self)

        # カスタムItem Modelの作成。
        model = DragDropItemModel()

        # カスタムTreeviewの作成。-----------------------------------------------------
        treeview = DragDropTreeView()
        treeview.setModel( model )
        # カラムの幅を指定する。
        treeview.setColumnWidth( 0, 400 )
        treeview.setColumnWidth( 1, 140 )
        treeview.setColumnWidth( 2, 100 )

        # treeviewを追加
        layout.addWidget( treeview )

        #  結合ボタンを追加
        button = QtGui.QPushButton("結合");
        self.connect(button,QtCore.SIGNAL('clicked()'),self.convine)
        layout.addWidget(button);

    def convine(self):
        print("convine start")
        if not url_list:
            return 0

        else:
            savename = QtGui.QFileDialog.getSaveFileName(self, 'Save file', '')
            #拡張子チェック
            if not savename in ('pdf'or 'PDF'):
                savename += '.pdf'
            fname = open(savename, 'w')

            cmd = 'pdftk '
            mojiretu = ' '.join(url_list) +(' cat output ') +savename
            cmd += mojiretu
            retcode = subprocess.check_call(cmd.split())
            print(retcode)

            QtGui.QMessageBox.information(self, "Message", "PDFの結合が完了しました。")
            self.show()
            return 0

if __name__ in '__main__':
    app    = QtGui.QApplication( sys.argv )
    window = MainWindow()
    window.show()

    sys.exit( app.exec_() )
