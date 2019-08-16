--
-- Name: gettopsearchhitname(integer, integer, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION gettopsearchhitname(integer, integer, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
   DECLARE
      seqobid ALIAS for $1;
      studyobid ALIAS for $2;
      argflag ALIAS for $3;
   BEGIN
      return getTopSearchHitAttribute(seqobid,studyobid,argflag,'NAME');
   END;
$_$;


ALTER FUNCTION public.gettopsearchhitname(integer, integer, character varying) OWNER TO agrbrdf;

