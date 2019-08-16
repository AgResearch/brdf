--
-- Name: getgeneidfromaccession(character varying, integer); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getgeneidfromaccession(character varying, integer) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
declare
   accession alias for $1;
   maxversion alias for $2;
   geneid int4;
begin
   select getAttributeFromAccession(accession, maxversion, 'geneid') into geneid;
   return geneid;
end;$_$;


ALTER FUNCTION public.getgeneidfromaccession(character varying, integer) OWNER TO agrbrdf;

