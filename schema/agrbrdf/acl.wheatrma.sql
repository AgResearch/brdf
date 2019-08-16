--
-- Name: wheatrma; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE wheatrma FROM PUBLIC;
REVOKE ALL ON TABLE wheatrma FROM agrbrdf;
GRANT ALL ON TABLE wheatrma TO agrbrdf;
GRANT SELECT ON TABLE wheatrma TO gbs;


