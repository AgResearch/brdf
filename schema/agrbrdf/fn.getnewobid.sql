--
-- Name: getnewobid(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getnewobid() RETURNS integer
    LANGUAGE plpgsql
    AS $$
   declare 
      mycur refcursor;
      newob integer;
   begin
      open mycur for 
      select nextval('ob_obidseq');
      fetch mycur into newob;
      return newob;
   end;
$$;


ALTER FUNCTION public.getnewobid() OWNER TO agrbrdf;

