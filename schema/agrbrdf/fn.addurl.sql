--
-- Name: addurl(integer, text, text, text, boolean); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION addurl(integer, text, text, text, boolean) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
   declare 
      urlon alias for $1;
      urltext alias for $2;
      urladdress alias for $3;
      author alias for $4;
      reuse alias for $5;
      mycur refcursor;
      existingurl integer;
      junk integer;
   begin


      if reuse then
         /* check if we can re-use a link */
         existingurl := null;
         open mycur for 
         select obid from uriob where uristring = urladdress;
         fetch mycur into existingurl;
         close mycur;
 
         if existingurl is null then
            existingurl := getNewObid();
            insert into uriob(obid, xreflsid, uristring, uritype)
            values (existingurl, urladdress, urladdress,'URL');
         end if;

         /* check if this object already commented with this comment */
         select ob into junk from urilink where uriob = existingurl and ob = urlon;
         if not FOUND then
            insert into urilink(ob,uriob,displaystring,createdby) values(urlon, existingurl,urltext,author);
         end if;

         return existingurl;
      else
         existingurl := getNewObid();
         insert into uriob(obid, xreflsid, uristring, uritype)
         values (existingurl, urladdress, urladdress,'URL');
         insert into urilink(ob,uriob,displaystring,createdby) values(urlon, existingurl,urltext,author);
      end if;

      return existingurl;
      
   end;
$_$;


ALTER FUNCTION public.addurl(integer, text, text, text, boolean) OWNER TO agrbrdf;

