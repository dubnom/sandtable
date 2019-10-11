from Sand import *
from os import getenv, listdir, rename, remove
from Chains import *
import cPickle as pickle

class History(object):
    @staticmethod
    def history( params, sandable, chains ):
        # Don't store history if the image is too simple
        if sum( map( len, chains )) < 8:
            return

        files = filter( lambda f: f.startswith( '_' ), listdir( STORE_PATH ))
        name = '_history%02d'
        sandFormat = name + '.sand'
        pngFormat  = name + '.png'
    
        # Delete history overflow
        if sandFormat % HISTORY_COUNT in files:
            History.delete( name % HISTORY_COUNT )
    
        # Shift the history files
        for n in range( HISTORY_COUNT )[::-1]:
            oldName = sandFormat % n
            if oldName in files:
                rename( STORE_PATH + oldName, STORE_PATH + sandFormat % (n + 1) )
                rename( STORE_PATH + pngFormat % n, STORE_PATH + pngFormat % (n + 1) )
    
        # Save the history
        History.save( params, sandable, chains, name % 0 )
    
    @staticmethod
    def save( params, sandable, chains, name ):
        params.sandable = sandable
        pickle.dump( params, file( "%s%s.sand" % (STORE_PATH, name), 'wb' ))
        boundingBox = [ (0.0, 0.0), (TABLE_WIDTH, TABLE_LENGTH) ]
        Chains.saveImage( chains, boundingBox, "%s%s.png" % (STORE_PATH, name), IMAGE_WIDTH / 2, IMAGE_HEIGHT / 2)
    
    @staticmethod
    def delete( name ):
        remove( "%s%s.sand" % (STORE_PATH, name))
        remove( "%s%s.png" % (STORE_PATH, name))
    
    @staticmethod
    def load( name ):
        params = pickle.load( file( "%s%s.sand" % (STORE_PATH, name), 'rb' ))
        return params

    @staticmethod
    def list():
        save = []
        history = []
        filenames = listdir( STORE_PATH )
        filenames.sort()
        for name in filenames:
            if name.endswith( 'sand' ):
                if name.startswith( '_' ):
                    history.append( name[:-5] )
                else:
                    save.append( name[:-5] )
        return (save, history)


class Memoize( object ):
    """Memoize is used to cache drawings"""
    def __init__( self ):
        try:
            with open( CACHE_FILE, 'rb' ) as f:
                self.sandable = pickle.load( f )
                self.params = pickle.load( f )
                self.chainLoc = f.tell()
        except:
            self.sandable = None
            self.params = None

    def match( self, sandable, params ):
        return self.sandable == sandable and all( a.startswith( '__' ) or getattr( self.params, a, None ) == getattr( params, a, None ) for a in dir( params ))

    def chains( self ):
        with open( CACHE_FILE, 'rb' ) as f:
            f.seek( self.chainLoc )
            return pickle.load( f )

    def save( self, sandable, params, chains ):
        with open( CACHE_FILE, 'wb' ) as f: 
            pickle.dump( sandable, f )
            pickle.dump( params, f )
            pickle.dump( chains, f )


