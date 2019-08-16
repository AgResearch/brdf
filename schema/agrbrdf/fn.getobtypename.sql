--
-- Name: getobtypename(integer); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getobtypename(integer) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
    DECLARE
        argtypeid ALIAS for $1;
        resultobtype varchar;
    BEGIN
        select into resultobtype lower(tablename) from obtype where obtypeid = argtypeid;
        if not FOUND then
           return NULL;
        else
           return resultobtype;
        end if;
    END;
$_$;


ALTER FUNCTION public.getobtypename(integer) OWNER TO agrbrdf;

--
-- Name: FUNCTION getobtypename(integer); Type: COMMENT; Schema: public; Owner: agrbrdf
--

COMMENT ON FUNCTION getobtypename(integer) IS 'This function returns the name of a type , given its numeric typeid';


