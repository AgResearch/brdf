--
-- Name: blastx_results_tophit_field(character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION blastx_results_tophit_field(character varying, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
   DECLARE
      sqlstmnt varchar;
      queryid alias for $1;
      attributename alias for $2;
      rec record;
   BEGIN
      sqlstmnt := 'select '
        || attributename || ' as selectedfield ' 
        || ' from blastx_results where queryid = '''  
        || queryid 
        || ''' order by evalue limit 1';
      for rec in execute sqlstmnt loop
         return rec.selectedfield;
         exit;
      end loop;
   END;
$_$;


ALTER FUNCTION public.blastx_results_tophit_field(character varying, character varying) OWNER TO agrbrdf;

