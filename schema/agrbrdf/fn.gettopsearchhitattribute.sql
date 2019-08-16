--
-- Name: gettopsearchhitattribute(integer, integer, character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION gettopsearchhitattribute(integer, integer, character varying, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
   DECLARE
      hitcursor refcursor;
      seqobid ALIAS for $1;
      studyobid ALIAS for $2;
      argflag ALIAS for $3;
      attributename ALIAS for $4;
      tophitattribute varchar(5196);
      tophit integer;
      topobservation integer;
   BEGIN
      if upper(attributename) != 'HITFROM' and upper(attributename) != 'HITTO' and upper(attributename) != 'EVALUE'  and
         upper(attributename) != 'QUERYFROM' and upper(attributename) != 'QUERYTO'  and upper(attributename) != 'NEWFLAG' and
         upper(attributename) != 'QUERYFRAME'  and upper(attributename) != 'HITSTRAND' then
         tophit := getTopSearchHit(seqobid,studyobid,argflag);
         tophitattribute := null;
         if tophit is not null then
            if upper(attributename) = 'NAME' then
               open hitcursor for 
               select sequencename from 
               biosequenceob where obid = tophit;
            elsif  upper(attributename) = 'NAME AND DESCRIPTION' then
               open hitcursor for 
               select coalesce(sequencename || ' ' || sequencedescription, sequencename) from 
               biosequenceob where obid = tophit; 
            elsif  upper(attributename) = 'DESCRIPTION' then
               open hitcursor for 
               select sequencedescription from 
               biosequenceob where obid = tophit; 
            else 
               raise Exception 'unknown attribute specification';
            end if;
            fetch hitcursor into tophitattribute;
            close hitcursor;
         end if;
      else 
         topobservation := getTopSearchObservation(seqobid,studyobid,argflag);
         tophitattribute := null;
         if topobservation is not null then
            if upper(attributename) = 'QUERYTO' then
               open hitcursor for 
               select to_char(queryto,'9999999999') from 
               sequencealignmentfact  where databasesearchobservation  = topobservation;
            elsif  upper(attributename) = 'QUERYFROM' then
               open hitcursor for 
               select to_char(queryfrom,'9999999999')  from 
               sequencealignmentfact  where databasesearchobservation  = topobservation;
            elsif upper(attributename) = 'HITTO' then
               open hitcursor for 
               select to_char(hitto,'9999999999') from 
               sequencealignmentfact  where databasesearchobservation  = topobservation;
            elsif  upper(attributename) = 'HITFROM' then
               open hitcursor for 
               select to_char(hitfrom,'9999999999')  from 
               sequencealignmentfact  where databasesearchobservation  = topobservation;
            elsif  upper(attributename) = 'QUERYFRAME' then
               open hitcursor for 
               select to_char(queryframe,'9999999999')  from 
               sequencealignmentfact  where databasesearchobservation  = topobservation;
            elsif  upper(attributename) = 'HITSTRAND' then
               open hitcursor for 
               select to_char(hitstrand,'9999999999')  from 
               sequencealignmentfact  where databasesearchobservation  = topobservation;
            elsif  upper(attributename) = 'EVALUE' then
               open hitcursor for 
               select format_evalue(hitevalue)  from 
               databasesearchobservation  where obid = topobservation;
            elsif  upper(attributename) = 'NEWFLAG' then
               open hitcursor for 
               select 
                  case
                     when upper(userflags) like '%NEW%' then 'New' 
                     else null
                  end 
               from  
               databasesearchobservation  where obid = topobservation; 
            else 
               raise exception 'unsupported attribute % ', attributename;
            end if;
 
            fetch hitcursor into tophitattribute;

            close hitcursor;
         end if;
      end if;
     
      return tophitattribute;
   END;
$_$;


ALTER FUNCTION public.gettopsearchhitattribute(integer, integer, character varying, character varying) OWNER TO agrbrdf;

--
-- Name: gettopsearchhitattribute(character varying, integer, character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION gettopsearchhitattribute(character varying, integer, character varying, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
   DECLARE
      hitcursor refcursor;
      seqobid int4;
      seqname ALIAS for $1;
      studyobid ALIAS for $2;
      argflag ALIAS for $3;
      attributename ALIAS for $4;
      tophitattribute varchar(5196);
      tophit integer;
      topobservation integer;
  BEGIN
      seqobid := null;

      select obid into seqobid from biosequenceob where sequencename = seqname;

      if seqobid is null then
          return null;
      else
          return getTopSearchHitAttribute(seqobid, studyobid,argflag,attributename);
      end if;
  END;
$_$;


ALTER FUNCTION public.gettopsearchhitattribute(character varying, integer, character varying, character varying) OWNER TO agrbrdf;

