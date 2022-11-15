const char * inet_ntop(int af, const void * restrict cp, char * restrict buf, socklen_t arg_len)
{
    
    char hook_buff[BUFF_SIZE];
    sprintf(hook_buff, "inet_ntop((%d;%s;%c;%c))", af, cp, '_', '_');
    int sfd = get_sfd();
    hook_log(sfd, hook_buff);

    
    const char * (*old_inet_ntop)(int af, const void * restrict cp, char * restrict buf, socklen_t arg_len);
    const char * result;
    old_inet_ntop = dlsym(RTLD_NEXT, "inet_ntop");
    result = old_inet_ntop(af, cp, buf, arg_len);

    
    sprintf(hook_buff, "==%s", result);
    sprintf(hook_buff + len(hook_buff), "%c", sep);
    hook_log(sfd, hook_buff);

    return result;

}
