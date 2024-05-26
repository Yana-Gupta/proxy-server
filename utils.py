import re

keywords = ["gambling",
            "casino",
            "betting",
                "poker", 
                "lottery", 
                "drug", 
                "cocaine", 
                "marijuana", 
                "heroin", 
                "narcotics", 
                ]



def filter_content(redis_connection, content):
    filtering_keywords = redis_connection.smembers('filtering_keywords')
    
    for keyword in filtering_keywords:
        if keyword in content:
            print(keyword)
            return False
    return True


BLOCKED_URLS = 'blocked_urls'



def is_url_blocked(redis_connection, url):
    return redis_connection.sismember('blocked_urls', url)


def validate_and_sanitize_url(url):
    url_pattern = re.compile(r'^https?://[^\s/$.?#].[^\s]*$')
    
    if url_pattern.match(url):
        return 200, url.strip()
    else:
        return 400, None
