import base64
import re

GOCD_PATTERN = (r"Stage\s*\[(\S*)\/\d*\/(\S*)\/\d*\]\s*"
                r"(passed|failed|is fixed|is broken)")
                
#BASE_TFS_URL_PATTERN = r"Tfs: (https:\/\/.*?)\\r"
                
        
