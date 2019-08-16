--
-- Name: gettopsearchobservation(integer, integer, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION gettopsearchobservation(integer, integer, character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
   DECLARE
      hitcursor refcursor;
      seqobid ALIAS for $1;
      studyobid ALIAS for $2;
      argflag ALIAS for $3;
      topobservation int4;
   BEGIN   
      if seqobid is null then
         return null;
      end if;

      if argflag is null then 
         open hitcursor for
           select
              dso.obid
            from 
               databasesearchobservation dso left outer join sequencealignmentfact saf on
               saf.databasesearchobservation = dso.obid
            where           
               dso.databasesearchstudy = studyobid and 
               dso.querysequence = seqobid 
            order by
               dso.hitevalue asc,
               saf.bitscore desc;
      else
         open hitcursor for 
           select
              dso.obid
            from 
               databasesearchobservation dso left outer join sequencealignmentfact saf on
               saf.databasesearchobservation = dso.obid
            where           
               dso.databasesearchstudy = studyobid and 
               dso.querysequence = seqobid and
               dso.userflags like '%'||argflag||'%'
            order by
               dso.hitevalue asc,
               saf.bitscore desc;
      end if;


      fetch hitcursor into topobservation;
      if not FOUND then
         topobservation := null;
      end if;
      close hitcursor;
      return topobservation;
    END;
$_$;


ALTER FUNCTION public.gettopsearchobservation(integer, integer, character varying) OWNER TO agrbrdf;

