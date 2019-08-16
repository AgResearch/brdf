--
-- Name: getdescriptivelistmembership(integer); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getdescriptivelistmembership(integer) RETURNS text
    LANGUAGE plpgsql
    AS $_$
   declare 
      myob alias for $1;
      result text;
   begin
      select 
         --agg_comma_concat(split_part(l.listdefinition,':',1)) into result 
         agg_comma_concat(l.listdefinition) into result 
      from
         listmembershiplink lml join oblist l on
         l.obid = lml.oblist
      where
         lml.ob = myob;
      return result;
   end;
$_$;


ALTER FUNCTION public.getdescriptivelistmembership(integer) OWNER TO agrbrdf;

