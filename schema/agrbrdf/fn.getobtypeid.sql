--
-- Name: getobtypeid(character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getobtypeid(character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
    DECLARE
        argtable ALIAS for $1;
        resultobtype integer;
    BEGIN
        select into resultobtype obtypeid from obtype where upper(tablename) = upper(argtable) and isvirtual = false;
        if not FOUND then
           return NULL;
        else
           return resultobtype;
        end if;
    END;
$_$;


ALTER FUNCTION public.getobtypeid(character varying) OWNER TO agrbrdf;

--
-- Name: FUNCTION getobtypeid(character varying); Type: COMMENT; Schema: public; Owner: agrbrdf
--

COMMENT ON FUNCTION getobtypeid(character varying) IS 'This function returns the numeric typeid, given the name of the type';


