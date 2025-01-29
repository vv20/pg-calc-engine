from main.store.core import clear_cache, read_store, write_store, DataType

# read the submodules to register the type adapters
import main.store.configuration
import main.store.googlesheets
import main.store.localcsvfile
import main.store.memory