--
-- Name: addcomment(integer, text, text); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION addcomment(integer, text, text) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
   declare 
      commenton alias for $1;
      commenttext alias for $2;
      author alias for $3;
      mycur refcursor;
      existingcomment integer;
      commentonlsid varchar(2048);
      junk integer;
   begin

      /* get the lsid of the commented object */
      select xreflsid||':comment' into commentonlsid from ob where obid = commenton;


      /* check if we can re-use a comment */
      existingcomment := null;
      open mycur for 
      select obid from commentob where commentstring = commenttext;
      fetch mycur into existingcomment;
      close mycur;

      if existingcomment is null then
         existingcomment := getNewObid();
         insert into commentob(obid, xreflsid, commentstring)
         values (existingcomment, commentonlsid, commenttext);
      end if;

      /* check if this object already commented with this comment */
      select ob into junk from commentlink where commentob = existingcomment and ob = commenton;
      if not FOUND then
         insert into commentlink(ob,commentob,commentby) values(commenton, existingcomment,author);
      end if;

      return existingcomment;
      
   end;
$_$;


ALTER FUNCTION public.addcomment(integer, text, text) OWNER TO agrbrdf;

--
-- Name: addcomment(integer, text, text, boolean); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION addcomment(integer, text, text, boolean) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
   declare 
      commenton alias for $1;
      commenttext alias for $2;
      author alias for $3;
      reuse alias for $4;
      mycur refcursor;
      existingcomment integer;
      commentonlsid varchar(2048);
      junk integer;
   begin

      /* get the lsid of the commented object */
      select xreflsid||':comment' into commentonlsid from ob where obid = commenton;

      if reuse then
         /* check if we can re-use a comment */
         existingcomment := null;
         open mycur for 
         select obid from commentob where commentstring = commenttext;
         fetch mycur into existingcomment;
         close mycur;
 
         if existingcomment is null then
            existingcomment := getNewObid();
            insert into commentob(obid, xreflsid, commentstring)
            values (existingcomment, commentonlsid, commenttext);
         end if;

         /* check if this object already commented with this comment */
         select ob into junk from commentlink where commentob = existingcomment and ob = commenton;
         if not FOUND then
            insert into commentlink(ob,commentob,commentby) values(commenton, existingcomment,author);
         end if;

         return existingcomment;
      else
         existingcomment := getNewObid();
         insert into commentob(obid, xreflsid, commentstring)
         values (existingcomment, commentonlsid, commenttext);
         insert into commentlink(ob,commentob,commentby) values(commenton, existingcomment,author);
      end if;

      return existingcomment;
      
   end;
$_$;


ALTER FUNCTION public.addcomment(integer, text, text, boolean) OWNER TO agrbrdf;

