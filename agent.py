# 1 ) https://supabase.com/docs/reference/python/introduction?queryGroups=platform&platform=conda
# grant access pour RPC ( la method est deja fait )
# faire le client + call RPC => et mettre ça dans un @Tool 
# faire un agent qui utilisera le tool









# TODO là en gros il faut : creer la method SQL dans supabase qui est une method SQL qui fait un search à la con sur la base vector 
# TODO => init le client + call RPC dans une method qui sera utilisé par un @Tool
# TODO => créer un agent qui va utiliser ce tool pour résoudre la question


# https://docs.langchain.com/oss/python/integrations/vectorstores/supabase?_gl=1*75dmu6*_gcl_au*MTk3MTA3MTI3Ni4xNzc2ODAwODQ0*_ga*MTgyMTUyMzYuMTc3NjgwMDg0NA..*_ga_47WX3HKKY2*czE3NzY5ODMxMDkkbzYkZzAkdDE3NzY5ODMxMDkkajYwJGwwJGgw


# TODO : https://docs.langchain.com/oss/python/langchain/tools
# create retriever ( RAG ) => just RPC call with supabase using sql method with embedding search 
# and agent will call the right tool 

