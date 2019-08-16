--
-- Name: ontologyfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE ontologyfact FROM PUBLIC;
REVOKE ALL ON TABLE ontologyfact FROM agrbrdf;
GRANT ALL ON TABLE ontologyfact TO agrbrdf;
GRANT SELECT ON TABLE ontologyfact TO gbs;


