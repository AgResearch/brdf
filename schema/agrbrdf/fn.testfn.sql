--
-- Name: testfn(integer); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION testfn(integer) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
   testvar integer[];
begin
   testvar[1] := 2;
   testvar[3] := 4;
end;
$$;


ALTER FUNCTION public.testfn(integer) OWNER TO agrbrdf;

