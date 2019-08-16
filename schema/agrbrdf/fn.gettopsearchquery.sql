--
-- Name: gettopsearchquery(integer, integer); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION gettopsearchquery(integer, integer) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
   DECLARE
      hitcursor refcursor;
      seqobid ALIAS for $1;
      studyobid ALIAS for $2;
      tophit int4;
   BEGIN   

      if seqobid is null then
         return null;
      end if;


      open hitcursor for
    select
          querysequence
        from 
           databasesearchobservation dso left outer join sequencealignmentfact saf on
           saf.databasesearchobservation = dso.obid
        where
           dso.databasesearchstudy = studyobid and 
           dso.hitsequence = seqobid
        order by
           dso.hitevalue asc,
           saf.bitscore desc;
      fetch hitcursor into tophit;
      if not FOUND then
         tophit := null;
      end if;
      close hitcursor;
      return tophit;
    END;
$_$;


ALTER FUNCTION public.gettopsearchquery(integer, integer) OWNER TO agrbrdf;

