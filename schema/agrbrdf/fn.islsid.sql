--
-- Name: islsid(text, text); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION islsid(text, text) RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
   DECLARE
      arglsidtype alias for $1;
      arglsid alias for $2;
   BEGIN
      if upper(arglsidtype) = 'AGRESEARCH CATTLE SEQUENCES' then
         if upper(arglsid) like 'CS34%' or 
            upper(arglsid) like 'CS20%' or 
            upper(arglsid) like 'CS14%' or 
            upper(arglsid) like 'AGRESEARCH.BOVINE%' 
            then
            return true;
         else
            return false;
         end if;
      else
         return true;
      end if;
   END;
$_$;


ALTER FUNCTION public.islsid(text, text) OWNER TO agrbrdf;

