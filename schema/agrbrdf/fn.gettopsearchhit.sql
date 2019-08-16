--
-- Name: gettopsearchhit(integer, integer); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION gettopsearchhit(integer, integer) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
   DECLARE
      seqobid ALIAS for $1;
      studyobid ALIAS for $2;
   BEGIN   
      return getTopSearchHit(seqobid, studyobid, null);
    END;
$_$;


ALTER FUNCTION public.gettopsearchhit(integer, integer) OWNER TO agrbrdf;

--
-- Name: gettopsearchhit(integer, integer, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION gettopsearchhit(integer, integer, character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
   DECLARE
      hitcursor refcursor;
      seqobid ALIAS for $1;
      studyobid ALIAS for $2;
      argflag ALIAS for $3;
      tophit int4;
      topobservation int4;
   BEGIN   
      select getTopSearchObservation(seqobid, studyobid, argflag) into topobservation;
      if topobservation  is null then
         return null;
      end if;

      select hitsequence into tophit from databasesearchobservation where obid = topobservation;

      return tophit;
    END;
$_$;


ALTER FUNCTION public.gettopsearchhit(integer, integer, character varying) OWNER TO agrbrdf;

--
-- Name: gettopsearchhit(character varying, integer, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION gettopsearchhit(character varying, integer, character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
   DECLARE
      hitcursor refcursor;
      seqname ALIAS for $1;
      seqobid int4;
      studyobid ALIAS for $2;
      argflag ALIAS for $3;
      tophit int4;
      topobservation int4;
   BEGIN   
      seqobid := null;

      select obid into seqobid from biosequenceob where sequencename = seqname;

      if seqobid is null then
          return null;
      else
          return getTopSearchHit(seqobid,studyobid,argflag);
      end if;
    END;
$_$;


ALTER FUNCTION public.gettopsearchhit(character varying, integer, character varying) OWNER TO agrbrdf;

