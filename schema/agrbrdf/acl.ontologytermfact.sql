--
-- Name: ontologytermfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE ontologytermfact FROM PUBLIC;
REVOKE ALL ON TABLE ontologytermfact FROM agrbrdf;
GRANT ALL ON TABLE ontologytermfact TO agrbrdf;
GRANT SELECT ON TABLE ontologytermfact TO gbs;


