--
-- Name: ontologytermfact2; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE ontologytermfact2 FROM PUBLIC;
REVOKE ALL ON TABLE ontologytermfact2 FROM agrbrdf;
GRANT ALL ON TABLE ontologytermfact2 TO agrbrdf;
GRANT SELECT ON TABLE ontologytermfact2 TO gbs;


