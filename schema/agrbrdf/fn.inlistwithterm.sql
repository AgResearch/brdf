--
-- Name: inlistwithterm(integer, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION inlistwithterm(integer, character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $_$  

DECLARE
   mycur refcursor;
   myob alias for $1;
   myterm alias for $2;
   myresult integer;
BEGIN  
   myresult := 0;

   open mycur for 
      select 1 from oblist where upper(listdefinition) like '%' ||upper(myterm)||'%'
      and exists (select 1 from listmembershiplink where oblist = oblist.obid and ob = myob);

   fetch mycur into myresult;

   if not found then
      myresult := 0;
   else 
      myresult := 1;
   end if;
   
   close mycur;

   return myresult;
END
$_$;


ALTER FUNCTION public.inlistwithterm(integer, character varying) OWNER TO agrbrdf;

